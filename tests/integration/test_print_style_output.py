import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from python.helpers.print_style import PrintStyle, DisplayStyle

def test_print_all_styles():
    print_style = PrintStyle()
    
    print("\nDisplaying all available styles:\n")
    
    for style in DisplayStyle:
        print_style.print(f"This is {style.name} style", style=style)
        
        # Split the sentence into words and stream each word
        sentence = f"This is {style.name} style (streamed)"
        for word in sentence.split():
            print_style.stream(f"{word} ", style=style)
        print()  # Add a newline after streaming
        
        print()  # Add a newline for better readability
    
    print("\nAdditional tests:\n")
    
    # Test hint and error methods
    print_style.hint("This is a hint message")
    print_style.error("This is an error message")
    
    # Test custom style
    custom_style = PrintStyle(bold=True, italic=True, underline=True, 
                              font_color="cyan", background_color="magenta")
    custom_style.print("This is a custom styled text")

if __name__ == "__main__":
    test_print_all_styles()