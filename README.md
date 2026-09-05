SOC Shift Automation Engine
A Python-based automation utility designed to eliminate manual bottlenecks in SOC (Security Operations Center) shift handoffs. This tool ingests raw ticketing exports, processes critical security alerts, leverages AI for incident summarization, and generates a structured, professional HTML shift handoff report.

Features
Automated Ticket Ingestion: Parses raw CSV exports containing active shift incidents.

AI-Powered Summarization: Integrates with OpenAI models to distill complex incident descriptions into clear root causes and recommended actions.

Secure Credential Management: Utilizes python-dotenv to ensure sensitive API keys and environment variables are never hardcoded into the source code.

Clean HTML Reporting: Automatically compiles shift data into a clean, standalone HTML document formatted for quick operational review during shift changeovers.