#!/usr/bin/env python3
"""
ChatGPT Terminal Chat
Interactive conversation with ChatGPT via Zendesk AI Gateway
"""

import os
import sys
import openai
from datetime import datetime
from pathlib import Path

# Colors for terminal
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ChatGPTTerminal:
    """Interactive terminal chat with ChatGPT"""

    def __init__(self):
        """Initialize the chat client"""
        self.api_key = self._load_api_key()
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://ai-gateway.zende.sk/v1"
        )
        self.conversation_history = []
        self.model = "gpt-4o-mini"  # Default model

    def _load_api_key(self):
        """Load API key from .env file"""
        env_path = Path('.env')

        if not env_path.exists():
            print(f"{Colors.RED}❌ Error: .env file not found{Colors.END}")
            print(f"{Colors.YELLOW}Please create .env file with:{Colors.END}")
            print("ZENDESK_AI_GATEWAY_KEY=your_key_here")
            sys.exit(1)

        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('ZENDESK_AI_GATEWAY_KEY='):
                    return line.split('=', 1)[1].strip()

        print(f"{Colors.RED}❌ Error: API key not found in .env{Colors.END}")
        sys.exit(1)

    def print_banner(self):
        """Print welcome banner"""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}   💬 ChatGPT Terminal - Zendesk AI Gateway{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
        print(f"{Colors.YELLOW}Commands:{Colors.END}")
        print(f"  {Colors.GREEN}/exit{Colors.END}    - Exit the chat")
        print(f"  {Colors.GREEN}/clear{Colors.END}   - Clear conversation history")
        print(f"  {Colors.GREEN}/model{Colors.END}   - Change model (gpt-4o-mini, gpt-4o, etc.)")
        print(f"  {Colors.GREEN}/history{Colors.END} - Show conversation history")
        print(f"  {Colors.GREEN}/save{Colors.END}    - Save conversation to file")
        print(f"\n{Colors.CYAN}Current model: {Colors.END}{Colors.BOLD}{self.model}{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

    def send_message(self, user_message):
        """Send a message and get response"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            # Call ChatGPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                max_tokens=2000,
                temperature=0.7
            )

            assistant_message = response.choices[0].message.content

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            return f"{Colors.RED}Error: {e}{Colors.END}"

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print(f"{Colors.GREEN}✓ Conversation history cleared{Colors.END}")

    def change_model(self):
        """Change the model"""
        print(f"\n{Colors.YELLOW}Available models:{Colors.END}")
        models = [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ]

        for i, model in enumerate(models, 1):
            current = " (current)" if model == self.model else ""
            print(f"  {i}. {model}{current}")

        try:
            choice = input(f"\n{Colors.CYAN}Select model (1-{len(models)}): {Colors.END}")
            idx = int(choice) - 1

            if 0 <= idx < len(models):
                self.model = models[idx]
                print(f"{Colors.GREEN}✓ Model changed to: {self.model}{Colors.END}")
            else:
                print(f"{Colors.RED}Invalid choice{Colors.END}")
        except (ValueError, KeyboardInterrupt):
            print(f"{Colors.YELLOW}Cancelled{Colors.END}")

    def show_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            print(f"{Colors.YELLOW}No conversation history yet{Colors.END}")
            return

        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}Conversation History ({len(self.conversation_history)} messages){Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")

        for i, msg in enumerate(self.conversation_history, 1):
            role = msg['role']
            content = msg['content']

            if role == 'user':
                print(f"{Colors.BLUE}👤 You:{Colors.END}")
            else:
                print(f"{Colors.GREEN}🤖 Assistant:{Colors.END}")

            print(f"{content}\n")

    def save_conversation(self):
        """Save conversation to file"""
        if not self.conversation_history:
            print(f"{Colors.YELLOW}No conversation to save{Colors.END}")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"outputs/logs/chatgpt_conversation_{timestamp}.txt"

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, 'w') as f:
            f.write(f"ChatGPT Terminal Conversation\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {self.model}\n")
            f.write("="*70 + "\n\n")

            for msg in self.conversation_history:
                role = "You" if msg['role'] == 'user' else "Assistant"
                f.write(f"{role}:\n{msg['content']}\n\n")

        print(f"{Colors.GREEN}✓ Conversation saved to: {filename}{Colors.END}")

    def run(self):
        """Main chat loop"""
        self.print_banner()

        try:
            while True:
                # Get user input
                user_input = input(f"{Colors.BLUE}{Colors.BOLD}You: {Colors.END}").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    command = user_input.lower()

                    if command == '/exit':
                        print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}\n")
                        break

                    elif command == '/clear':
                        self.clear_history()
                        continue

                    elif command == '/model':
                        self.change_model()
                        continue

                    elif command == '/history':
                        self.show_history()
                        continue

                    elif command == '/save':
                        self.save_conversation()
                        continue

                    else:
                        print(f"{Colors.RED}Unknown command: {user_input}{Colors.END}")
                        print(f"{Colors.YELLOW}Type /exit, /clear, /model, /history, or /save{Colors.END}")
                        continue

                # Send message and get response
                print(f"\n{Colors.GREEN}{Colors.BOLD}🤖 Assistant: {Colors.END}", end="")
                response = self.send_message(user_input)
                print(response)
                print()

        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}👋 Chat interrupted. Goodbye!{Colors.END}\n")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}\n")


def main():
    """Run the chat"""
    chat = ChatGPTTerminal()
    chat.run()


if __name__ == '__main__':
    main()
