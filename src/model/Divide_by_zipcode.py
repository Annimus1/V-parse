import os
import pandas as pd
import rich_click as click


def Divide_by_zipcode(dirpath: str, column_name: str = "Zip") -> None:
    """
    Scans a directory for CSV files and processes each one to split it by zipcode.
    
    Args:
        dirpath (str): Path to the directory containing CSV files.
        column_name (str): Name of the column used for grouping (e.g., 'Zip').
    """
    if not os.path.exists(dirpath):
        click.echo(click.style(text=f"🛑 Error: Directory {dirpath} not found.", fg="red"))
        return

    # Scan the folder for CSV files
    with os.scandir(dirpath) as entries:
        for entry in entries:
            # Avoid processing files already created by the script (starting with 'zip_')
            if entry.is_file() and entry.name.endswith(".csv") and not entry.name.startswith("zip_"):
                Divide(entry.path, column_name, dirpath)

def Divide(file_path: str, column_name: str, target_dir: str) -> None:
    """
    Function to split a single CSV by zipcode using pandas vectorization.
    
    Args:
        file_path (str): Full path to the source CSV file.
        column_name (str): The column to group by.
        target_dir (str): Destination directory for the output files.
    """
    click.echo(click.style(text=f"⚠️ Processing file: {os.path.basename(file_path)}", fg="yellow"))
    
    try:
        # Load the data - low_memory=False to handle mixed types in columns
        df = pd.read_csv(file_path, low_memory=False)

        if column_name not in df.columns:
            click.echo(click.style(text=f"🛑 Skipping: Column '{column_name}' not found.", fg="red"))
            return

        grouped = df.groupby(column_name)

        for zipcode, group_df in grouped:
            # Handle potential float zipcodes (e.g., 28227.0 -> 28227)
            try:
                clean_zip = str(int(float(zipcode)))
            except (ValueError, TypeError):
                clean_zip = str(zipcode).strip()

            output_filename = f"zip_{clean_zip}.csv"
            output_path = os.path.join(target_dir, output_filename)

            # Check if file exists to determine if we need to write the header
            file_exists = os.path.isfile(output_path)

            # mode='a' appends data if the file already exists
            # header=not file_exists ensures headers are only written the first time
            group_df.to_csv(
                output_path, 
                mode='a', 
                index=False, 
                header=not file_exists, 
                encoding='utf-8'
            )

        click.echo(click.style(text=f"✅ Done: {os.path.basename(file_path)} split successfully.", fg="red"))    

    except Exception as e:
        click.echo(click.style(text=f"🛑 An error occurred while processing {file_path}: {e}", fg="green"))