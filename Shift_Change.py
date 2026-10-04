import os
import datetime
from pathlib import Path
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load variables from the local .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Initialize the OpenAI client
# ---------------------------------------------------------------------------
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)
# ---------------------------------------------------------------------------
# AI Summary
# ---------------------------------------------------------------------------
def summarize_ticket_with_ai(ticket_title, ticket_description):
    #Sends a raw ticket description to the AI API and returns a concise 2-bullet executive summary.
    prompt = f"""
    You are an expert Cyber Threat Intelligence Analyst helping summarize shift logs for a SOC handoff report.
    
    Ticket Title: {ticket_title}
    Raw Description: {ticket_description}
    
    Task: Provide a concise, professional 2-sentence summary of this incident for the incoming shift analyst.
    Focus on:
    1. Root cause / trigger event.
    2. Current remediation status or immediate next action required.
    
    Do NOT include filler text. Output only the summary points.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise cybersecurity operational reporting assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Low temperature ensures factual, consistent outputs without creative halluncinations
            max_tokens=150 # Keep response short.
        )
        summary = response.choices[0].message.content.strip()
        return summary
    
    except Exception as e:
        print(f"[!] AI API call failed for ticket '{ticket_title}': {e}")
        return "Summary unavailable (API error)."

# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------
def generate_html_report(dataframe, output_filename="shift_handoff_report.html"):
    """
    Takes the processed Pandas DataFrame and injects it into a styled, Dark-Mode HTML template.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_tickets = len(dataframe)

    # Building Ticket Cards HTML Dynamically
    ticket_cards_html = ""
    for _, row in dataframe.iterrows():
        ticket_id = row.get('Ticket_ID', 'N/A')
        title = row.get('Title', 'No Title')
        status = row.get('Status', 'OPEN').upper()
        summary = row.get('AI_Shift_Summary', 'No summary available.')
        raw_desc = row.get('Description', 'No raw description provided.')

        # Set status badge color dynamically
        badge_class = "badge-open" if status == "OPEN" else "badge-closed"

        card = f"""
        <div class="ticket-card">
            <div class="ticket-header">
                <span class="ticket-id">{ticket_id}</span>
                <span class="ticket-title">{title}</span>
                <span class="badge {badge_class}">{status}</span>
            </div>
            <div class="summary-section">
                <strong>🤖 AI Handoff Executive Summary:</strong>
                <p>{summary}</p>
            </div>
            <details class="raw-details">
                <summary>View Raw Incident Logs / Full Description</summary>
                <p>{raw_desc}</p>
            </details>
        </div>
        """
        ticket_cards_html += card

    script_dir = Path(__file__).resolve().parent
    template_path = script_dir / "templates" / "shift_report_template.html"

    if not template_path.exists():
        print(f"[X] Error: Template file not found at {template_path}")
        return

    # Read external template file
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # Safely inject variables via replacement to avoid CSS/Python brace conflicts
    html_content = (
        template_content
        .replace("{NOW}", now)
        .replace("{TOTAL_TICKETS}", str(total_tickets))
        .replace("{TICKET_CARDS_HTML}", ticket_cards_html)
    )
    
    # Write HTML output to disk
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n[🚀 SUCCESS] Shift Handoff Report generated: {os.path.abspath(output_filename)}")

# ---------------------------------------------------------------------------
# Pipeline execution 
# ---------------------------------------------------------------------------
def process_shift_handoff(csv_file_path):
    """
    Phase 1 + Phase 2 Pipeline:
    1. Reads ticket CSV
    2. Filters open tickets
    3. Iterates through tickets and appends AI summaries
    """
    if not os.path.exists(csv_file_path):
        print(f"[X] Error: File '{csv_file_path}' not found.")
        return None

    print(f"[*] Reading ticket export from: {csv_file_path}")
    df = pd.read_csv(csv_file_path)

    # Filter for active tickets if column exists
    if 'Status' in df.columns:
        active_tickets = df[df['Status'].str.upper() == 'OPEN'].copy()
    else:
        active_tickets = df.copy()

    print(f"[+] Processing {len(active_tickets)} active tickets with AI summarization...\n")

    # Array to hold generated summaries
    ai_summaries = []

    # Iterate through each row in the dataframe
    for index, row in active_tickets.iterrows():
        title = row.get('Title', 'No Title')
        description = row.get('Description', 'No Description Provided')

        print(f" -> Summarizing Ticket ID {row.get('Ticket_ID', index)}: {title}...")
        
        # Call Phase 2 AI Function
        summary = summarize_ticket_with_ai(title, description)
        ai_summaries.append(summary)

    # Add the new AI summaries as a distinct column in our Pandas Dataframe
    active_tickets['AI_Shift_Summary'] = ai_summaries

    print("\n[+] AI Summarization Complete!")
    return active_tickets


# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    # Test file name
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_csv = os.path.join(script_dir, "cybersecurity_tickets_mock.csv")
    
    # Process tickets
    summary_df = process_shift_handoff(sample_csv)

    if summary_df is not None:
        # Display the results in terminal
        print("\n=== PROCESSED SHIFT HANDOFF DATA ===")
        print(summary_df[['Ticket_ID', 'Title', 'AI_Shift_Summary']])

        generate_html_report(summary_df)
