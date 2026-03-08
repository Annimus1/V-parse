# Author: Pablo Vergara
#!/usr/bin/python3
import os
import rich_click as click
from util import Util
from model.Parser import Parser
from model.Divide_by_zipcode import Divide_by_zipcode


@click.command()
@click.argument('filename', required=True, type=click.Path(exists=False))
def main(filename):
    """
    Main entry point for the V-Parse CLI tool.

    This tool helps you validate, clean, and format CSV files for Vicidial database import.
    You can inspect headers, organize phone columns, remove unnecessary columns, and save the processed file.

    Args:
        filename (str): Path to the CSV file to process.
    """
    if(os.path.isdir(filename)):
        column_name = input("Please provide column name to divide (Enter => 'Zip'): ")
        
        Divide_by_zipcode(filename) if not column_name else Divide_by_zipcode(filename, column_name)
        
    else:
        # Option selected by the user
        option = ''
        # DataFrame that will contain the result file
        global result

        # Create Parser instance
        parser = Parser(filename)

        # Display headers to the user
        Util.Show_headers(parser.get_filename(), parser.get_headers())

        while True:
            # Division line
            print("")

            # Show available actions
            click.echo("Available actions:")
            click.echo(click.style(text="1) ", fg="green") + "Show Headers")
            click.echo(click.style(text="2) ", fg="yellow") + "Fill up phones")
            click.echo(click.style(text="3) ", fg="red") + "Remove columns")
            click.echo(click.style(text="4) ", fg="blue") + "Vicidialize")
            click.echo(click.style(text="5) ", fg="red") + "Filter")
            click.echo(click.style(text="6) ", fg="cyan") + "Save")
            click.echo(click.style(text="0) ", fg="white") + "Exit")

            try:
                option = int(input("-> "))

                if option == 1:
                    # Show Headers
                    # Clear the terminal screen based on OS
                    if os.name == 'nt':
                        _ = os.system('cls')  # For Windows
                    else:
                        _ = os.system('clear')  # For Linux/macOS

                    Util.Show_headers(parser.get_filename(), parser.get_headers())
                    continue

                elif option == 2:
                    # Fill up Phone columns
                    phone_column = int(input("Enter Phone Column > "))
                    alt_column = int(input("Enter Alternative Phone Column > "))

                    # Ask for additional phone columns
                    msg = "Enter additional phone columns (separated by commas) > "
                    phones_columns = input(msg)
                    phones_columns = [int(p.strip())
                                    for p in phones_columns.split(',')]

                    # Ask for additional alternative phone columns
                    msg = "Enter additional alt_phone columns (separated by commas) > "
                    alt_phones_columns = input(msg)
                    alt_phones_columns = [int(p.strip())
                                        for p in alt_phones_columns.split(',')]

                    # Call parser method
                    result = parser.Fillup_phones(
                        phone_column,
                        alt_column,
                        phones_columns,
                        alt_phones_columns
                    )
                    parser.set_current_dataframe(result)
                    # Update headers
                    parser.set_current_headers()

                    input("Press Enter to continue")
                    continue

                elif option == 3:
                    # Remove columns
                    prompt = "Enter columns you would like to keep (separated by commas): "
                    keep_columns = input(prompt)
                    keep_columns = [int(p.strip())
                                    for p in keep_columns.split(',')]

                    # Call parser method to remove unused columns
                    parser.RemoveUnusedColumns(keep_columns)
                    input("Press Enter to continue")
                    continue

                elif option == 4:
                    # Vicidialize
                    prompt = "Enter column from current Phone: "
                    phone = int(input(prompt))

                    prompt = "Enter column from current Alt Phone: "
                    alt = int(input(prompt))

                    parser.Vicidialize(phone, alt)
                    continue

                elif option == 5:
                    # Filter
                    prompt = "Enter Target column: "
                    target = int(input(prompt))

                    prompt = "Enter values to filter separated by commas: "
                    values = input(prompt)
                    values = values.split(',')

                    if len(values) == 1 and values[0] == '':
                        click.echo(click.style(text='Amount of values can not be 0 ',bg='red', bold=True))
                    
                    parser.Filter_by(target, values)

                    continue

                elif option == 6:
                    # Save the current DataFrame
                    parser.Save()
                    break

                elif option == 0:
                    # Exit the program
                    break

                else:
                    raise ValueError

            except ValueError:
                click.echo(click.style(
                    text="Invalid Option.", fg="red", bold=True))
                click.echo(click.style(
                    text="Please use numbers only.", fg="red", bold=True))


if __name__ == "__main__":
    main()
