from crew import AgileCrew
import gradio as gr
from gradio.themes.utils import sizes
from dbtunnel import dbtunnel

# Backend function for AGILE team kickoff
def kickoff_crew(message, history):
    # If no input, trigger `crew.kickoff()` without inputs
    if len(message.strip()) == 0:
        try:
            result = AgileCrew().crew().kickoff()  # Call without inputs if no message
            result = result.raw
            
            # Truncate if result is too long
            max_length = 5000
            if len(result) > max_length:
                result = result[:max_length] + "... [Output Truncated]"

            response_data = f"AGILE Agent started successfully. Result: {result}"
            print(response_data)

        except Exception as e:
            response_data = f"An error occurred during crew kickoff: {e}"
            print(response_data)

        return response_data

    # Proceed with normal kickoff if message is provided
    try:
        inputs = {"question": message}
        result = AgileCrew().crew().kickoff(inputs=inputs)
        result = result.raw

        max_length = 5000
        if len(result) > max_length:
            result = result[:max_length] + "... [Output Truncated]"

        response_data = f"Process triggered successfully. Result: {result}"
        print(response_data)

    except Exception as e:
        response_data = f"An error occurred during crew kickoff: {e}"
        print(response_data)

    return response_data

def run():
        # Gradio theme and layout customization
        theme = gr.themes.Soft(
        text_size=sizes.text_sm, radius_size=sizes.radius_sm, spacing_size=sizes.spacing_sm,
        )

        # Define the Gradio ChatInterface
        demo = gr.ChatInterface(
        fn=kickoff_crew,  # Connect to backend function
        chatbot=gr.Chatbot(show_label=False, container=False, show_copy_button=True, bubble_full_width=True),
        textbox=gr.Textbox(placeholder="Ask a question or start the AGILE Agent", container=False, scale=7),
        title="AgileGenius",
        description="Trigger the AGILE Team Agent by entering a question or clicking 'Start AGILE Team'.",
        submit_btn="Start AGILE Team",  # Custom submit button
        clear_btn="Clear",  # Reset chat history
        )
        dbtunnel.gradio(demo).run()

if __name__ == '__main__':
    run()


