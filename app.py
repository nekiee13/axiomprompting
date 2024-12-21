import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
import structlog
import logging
import re
from ollama import chat

# Import modularized data
from Core import CORE_PARAMETERS
from Vectors import VECTORS
from Response_Generation_Protocol import RESPONSE_GENERATION_STEPS

# Import Ollama model configuration
from LLM_model import OLLAMA_MODEL_CONFIG

# Load environment variables
dotenv_path = find_dotenv()  # Find the .env file
if not dotenv_path:
    raise FileNotFoundError("The .env file is missing. Please create it.")

load_dotenv(dotenv_path, verbose=True)  # Load the .env file with verbose logging

# Initialize Rich and StructLog
console = Console()
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler()])
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger()

# Function to parse user input
def parse_user_input(user_input):
    """Parse the user input with nested parentheses into a structured dictionary."""
    parsed_input = {}

    # Regex to match the outer structure param(attrs)
    outer_pattern = r"(\w+)\((.+?)\)"
    matches = re.findall(outer_pattern, user_input)

    for param_name, nested_attrs in matches:
        if param_name not in parsed_input:
            parsed_input[param_name] = {}

        # Regex to handle nested attributes inside parentheses
        inner_pattern = r"(\w+)\((.+?)\)"
        nested_matches = re.findall(inner_pattern, nested_attrs)

        for attr_name, values in nested_matches:
            if attr_name not in parsed_input[param_name]:
                parsed_input[param_name][attr_name] = []
            parsed_input[param_name][attr_name].extend(values.split(" & "))

    return parsed_input

# Function to fetch selected data dynamically
def fetch_selected_data(parsed_input, core_data, vectors_data, response_data):
    """Fetch the selected parameters, attributes, and values from the modularized files."""
    selected_data = {}
    for param, attrs in parsed_input.items():
        if param in core_data:
            selected_data[param] = {attr: core_data[param][attr] for attr in attrs}
        elif param in vectors_data:
            selected_data[param] = {attr: vectors_data[param][attr] for attr in attrs}
        elif param in response_data:
            selected_data[param] = {attr: response_data[param][attr] for attr in attrs}
    return selected_data

# Function to validate the user's query
def validate_query(query):
    """Validate the user's query to ensure it is appropriately formatted."""
    if not isinstance(query, str) or len(query.strip()) == 0:
        raise ValueError("Query must be a non-empty string.")

# Function to generate the simplified prompt
def generate_simplified_prompt(query, optimization_parameters=None, generation_steps=None):
    """Generate a simplified and clear axiom-based prompt."""
    validate_query(query)

    optimization_parameters = optimization_parameters or {}
    generation_steps = generation_steps or RESPONSE_GENERATION_STEPS

    # Construct the simplified prompt
    prompt = f"""
Objective: Provide a comprehensive and accurate response to the query: "{query}".

Optimization Parameters:
"""
    for param, attrs in optimization_parameters.items():
        prompt += f"- {param}:\n"
        for attr, values in attrs.items():
            prompt += f"  - {attr}: {', '.join(values)}\n"

    prompt += "\nResponse Generation Steps:\n"
    for step, values in generation_steps.items():
        prompt += f"- {step}: {', '.join(values)}\n"

    return prompt

# Function to submit the prompt to Ollama
def submit_to_ollama(prompt, model, ctx_window_size=2048, axiom_request=""):
    """
    Submit the formatted prompt to Ollama and retrieve the response.

    Args:
        prompt (str): The prompt to submit to the model.
        model (str): The name of the model to use (e.g., "qwq:latest").
        ctx_window_size (int): Controls the context window size (default: 2048).
        axiom_request (str): The axiom request to include as the first line of the file.

    Raises:
        Exception: If the Ollama request fails.
    """
    try:
        logger.info(f"Submitting prompt to Ollama with model: {model}")
        logger.info(f"Hyperparameters: ctx_window_size={ctx_window_size}")

        # Submit the prompt to Ollama
        stream = chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        # Save the response to a file with a timestamped filename
        timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
        filename = f"{timestamp}.md"
        with open(filename, "w") as file:
            # Write the axiom request as the first line
            file.write(f"Axiom request: {axiom_request}\n\n")
            for chunk in stream:
                content = chunk['message']['content']
                print(content, end='', flush=True)  # Print to console
                file.write(content)  # Write to file

        logger.info(f"Response saved to {filename}")

    except Exception as e:
        logger.error(f"Ollama request failed: {e}")
        raise Exception(f"Ollama request failed: {e}")

# Function to interpret the axiom
def interpret_axiom(parsed_input, core_data):
    """Interpret the axiom request into a human-readable format."""
    interpretation = []
    for param, attrs in parsed_input.items():
        param_name = next((k for k, v in core_data.items() if k.startswith(param)), None)
        if not param_name:
            continue
        interpretation.append(f"{param_name}(")
        for attr, values in attrs.items():
            attr_name = next((k for k, v in core_data[param_name].items() if k.startswith(attr)), None)
            if not attr_name:
                continue
            interpretation.append(f"  {attr_name}({', '.join(values)})")
        interpretation[-1] += ")"
    return " + ".join(interpretation)

# Function to prompt user for confirmation
def confirm_setup():
    """Prompt the user to confirm the axiom setup."""
    console.print("[bold yellow]Do you want to confirm the axiom setup and continue?\n0. Yes [0]\n1. No [1][/bold yellow]")
    response = input("Enter your choice (0 or 1): ").strip()
    if response == "0":
        return True
    elif response == "1":
        console.print("[bold red]Exiting the app. Please modify the setup and restart.[/bold red]")
        exit()
    else:
        console.print("[bold red]Invalid response. Please enter '0' or '1'.[/bold red]")
        return confirm_setup()

# Function to read user query from file
def read_user_query(file_path):
    """Read the user query from a file."""
    try:
        with open(file_path, "r") as file:
            query = file.read().strip()
            if not query:
                raise ValueError("The file is empty. Please provide a valid query.")
            return query
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' does not exist. Please create the file and add the query.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")

# Main application logic
def main():
    # Load axiom input from .env
    axiom_input = os.getenv("AXIOM", "")

    # Read user query from file
    try:
        user_query = read_user_query("user_query.md")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return

    try:
        # Parse the axiom input
        parsed_input = parse_user_input(axiom_input)

        # Interpret the axiom
        axiom_interpretation = interpret_axiom(parsed_input, CORE_PARAMETERS)
        console.print(f"[bold green]Axiom request:[/bold green] {axiom_input}")
        console.print(f"[bold green]Axiom setup interpretation:[/bold green] {axiom_interpretation}")

        # Prompt user to confirm setup
        if not confirm_setup():
            return

        # Fetch the selected data dynamically
        selected_data = fetch_selected_data(parsed_input, CORE_PARAMETERS, VECTORS, RESPONSE_GENERATION_STEPS)

        # Generate the simplified prompt
        simplified_prompt = generate_simplified_prompt(user_query, optimization_parameters=selected_data)
        console.print("[bold green]Generated Simplified Prompt:[/bold green]")
        console.print(simplified_prompt)

        # Submit to Ollama with custom hyperparameters
        submit_to_ollama(
            prompt=simplified_prompt,
            axiom_request=axiom_input,  # Pass the axiom request
            model=OLLAMA_MODEL_CONFIG["model"],
            ctx_window_size=OLLAMA_MODEL_CONFIG["ctx_window_size"]
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

# Entry point
if __name__ == "__main__":
    main()