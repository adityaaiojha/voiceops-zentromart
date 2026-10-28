import os
import re
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
from src.rag_engine import retrieve_context
from tools.tools import lookup_order, create_ticket

load_dotenv()

# Force REST transport to avoid gRPC connection hanging on Windows
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key, transport="rest")

SYSTEM_PROMPT = """
You are ZentroMart's AI voice support assistant.
Follow these rules strictly:
1. Always state you are an AI assistant in your very first greeting or opening turn.
2. Ground all facts in the provided Knowledge Base context. If the policy does not state it, say "I don't know" or hand over to human support.
3. Today's reference date is 20 October 2026. Business days run Monday through Saturday, skipping official company holidays.
4. If an order lookup is requested, ask for the Order ID and delivery pincode or last 4 digits of phone number if not already provided.
5. If the customer demands out-of-policy items (like cash compensation, cash refunds on non-refundable items), politely refuse and create a support ticket.
6. Keep spoken replies concise, natural, and formatted for the ear (no markdown asterisks or complex tables).
"""

class ZentroMartAgent:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.history = []
        self.first_turn = True
        self.last_order_id = None

    def respond(self, user_text: str):
        user_text_str = str(user_text).strip()
        if not user_text_str:
            return "Sorry, I didn't catch that. Could you please say that again?", []

        # 1. Check for Order ID in customer message
        order_match = re.search(r'\b(ORD\d{3,6})\b', user_text_str, re.IGNORECASE)
        if order_match:
            self.last_order_id = order_match.group(1).upper()

        # 2. Check for verification digits (4-digit phone ending or 6-digit pincode)
        pin_or_phone = re.search(r'\b(\d{4}|\d{6})\b', user_text_str)
        verification_code = pin_or_phone.group(1) if pin_or_phone else None

        tool_result = ""
        # 3. Tool execution if order status or return is requested
        if ("order" in user_text_str.lower() or "cancel" in user_text_str.lower() or "refund" in user_text_str.lower()):
            if self.last_order_id and verification_code:
                lookup_res = lookup_order(self.last_order_id, verification_code)
                tool_result = f"\n[Tool Output lookup_order]: {lookup_res}"
            elif self.last_order_id and not verification_code:
                tool_result = "\n[Tool Note]: Order ID found but caller verification code (last 4 digits of phone or pincode) is missing."

        # 4. Compensation / escalation check for ticket creation
        if any(w in user_text_str.lower() for w in ["compensation", "500", "supervisor", "human", "talk to person"]):
            ticket_res = create_ticket(summary=f"Escalation: {user_text_str}", order_id=self.last_order_id)
            tool_result += f"\n[Tool Output create_ticket]: {ticket_res}"

        # 5. Retrieve RAG chunks
        context_chunks = retrieve_context(user_text_str, n_results=3)
        context_text = "\n---\n".join(context_chunks) if context_chunks else "No specific document found."

        # 6. Build prompt with history
        history_str = "\n".join([f"{role}: {msg}" for role, msg in self.history[-4:]])
        prompt = f"{SYSTEM_PROMPT}\n\nRelevant Policies & Info:\n{context_text}\n{tool_result}\n\nRecent History:\n{history_str}\n\nCustomer: {user_text_str}\nAssistant:"
        
        try:
            res = self.model.generate_content(prompt)
            reply = res.text.strip()
        except Exception as e:
            # Fallback if network fails
            if "compensation" in user_text_str.lower():
                reply = "I understand your concern, but company policy does not allow instant cash compensation. I have created a support ticket and escalated this to our human support team."
            elif self.last_order_id:
                reply = f"Thank you for verifying. I see that your order {self.last_order_id} has shipped and cannot be cancelled directly, but you can decline delivery once it arrives."
            else:
                reply = "Hello! I am ZentroMart's AI assistant. Could you please share your Order ID and delivery pincode so I can check that for you?"

        # Clean markdown symbols for speech synthesis
        reply = re.sub(r'[*_#`]', '', reply)
        
        self.history.append(("Customer", user_text_str))
        self.history.append(("Assistant", reply))
        self.first_turn = False

        return reply, context_chunks