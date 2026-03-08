# Author: Pablo Vergara
import pandas as pd
from os import path, getcwd
from rich_click import echo, style
from typing import List
from model.Serializable import Serializable


class Parser(Serializable):
    """
    Parser class for handling CSV files and performing data cleaning operations.

    This class provides methods to:
    - Load and manage CSV data.
    - Clean and format phone numbers for Vicidial.
    - Remove or keep specific columns.
    - Fill missing phone numbers from alternative columns.
    - Filter rows by column values.
    - Save the processed data to a new CSV file.

    Attributes:
        fullPath (str): Absolute path to the file.
        filename (str): Name of the file.
        original_headers (list): List of original column headers.
        df (pd.DataFrame): Current DataFrame loaded from the file.
    """

    def __init__(self, filename: str):
        """
        Initialize the Parser object.

        Args:
            filename (str): Path to the CSV file.
        """
        self.fullPath = path.abspath(filename)
        self.filename = path.basename(self.fullPath)
        self.original_headers = []
        self.df = pd.read_csv(filename, low_memory=False)
        self.original_headers = self.df.columns.values

    def set_current_dataframe(self, new_data_frame: pd.DataFrame) -> None:
        """
        Set the current DataFrame.

        Args:
            new_data_frame (pd.DataFrame): DataFrame to set as current.
        """
        self.df = new_data_frame

    def get_current_dataframe(self) -> pd.DataFrame:
        """
        Get the current DataFrame.

        Returns:
            pd.DataFrame: The current DataFrame.
        """
        return self.df

    def get_headers(self) -> list:
        """
        Get the original headers of the DataFrame.

        Returns:
            list: List of column headers.
        """
        return self.original_headers

    def get_filename(self) -> str:
        """
        Get the filename.

        Returns:
            str: The filename.
        """
        return self.filename

    def set_current_headers(self) -> None:
        """
        Update the original headers to match the current DataFrame columns.
        """
        self.original_headers = self.df.columns.values

    def Save(self) -> None:
        """
        Save the current DataFrame to a CSV file in the working directory.

        The output file will be named 'Cleaned_{filename}'.

        On success, prints a confirmation message. On failure, prints an error message.
        """
        filename = f"Cleaned_{self.filename}"
        output = path.join(getcwd(), filename)

        try:
            self.df.to_csv(output, index=False)
            echo(style(text=f"File saved successfully: {output}", bold=True, fg="green"))
        except IOError:
            echo(style(
                text="There was a problem\nThe file could not be processed", bold=True, fg="red"))

    def RemoveUnusedColumns(self, columnsToKeep: List[int]) -> None:
        """
        Remove all columns except those specified by their indices.

        Args:
            columnsToKeep (List[int]): List of column indices to keep.

        On success, updates the DataFrame and headers, and prints a confirmation message.
        On failure, prints an error message.
        """
        columns = []
        try:
            # Build list of columns to keep by index
            for i in columnsToKeep:
                columns.append(self.original_headers[i])

            # Create new DataFrame with selected columns
            new_df = self.df[columns]
            self.set_current_dataframe(new_df)
            self.set_current_headers()
            echo(style(text=f"Dataframe updated successfully -> Columns: {columns}",
                       fg="green", bold=True))
        except IndexError:
            echo(style(text="Some columns don't match, please try again.",
                       fg="red", bold=True))

    def Fillup_phones(self, phone_column: int, alt_column: int,
                      phones_columns: List[int],
                      alt_phones_columns: List[int]) -> pd.DataFrame:
        """
        Fill missing phone and alternative phone numbers from specified columns.

        Args:
            phone_column (int): Index of the main phone column.
            alt_column (int): Index of the alternative phone column.
            phones_columns (List[int]): List of indices for phone alternatives.
            alt_phones_columns (List[int]): List of indices for alt phone alternatives.

        Returns:
            pd.DataFrame: Updated DataFrame with filled phone columns.

        For each row, if the main phone or alt phone is missing, tries to fill it from the provided alternatives.
        """
        for index, row in self.df.iterrows():
            # Fill main phone if missing
            if pd.isna(row[self.original_headers[phone_column]]):
                alternatives = phones_columns + [alt_column]
                self.df.iloc[index, phone_column] = self._fill_collum(index, alternatives)
                if pd.isna(self.df.iloc[index, phone_column]):
                    echo(style(text=f"[{index}] Phone not updated.", fg="red"))
                else:
                    echo(style(text=f"[{index}] Phone updated: {str(self.df.iloc[index, phone_column])}", fg="yellow"))

            # Fill alternative phone if missing
            if pd.isna(row[self.original_headers[alt_column]]):
                self.df.iloc[index, phone_column] = self._fill_collum(index, alt_phones_columns)
                if pd.isna(self.df.iloc[index, phone_column]):
                    echo(style(text=f"[{index}] Alt Phone not updated.", fg="red"))
                else:
                    echo(style(text=f"[{index}] Alt Phone updated: {str(self.df.iloc[index, phone_column])}", fg="yellow"))

        return self.df

    def _fill_collum(self, index: int, alternatives: List[int]) -> str | None:
        """
        Helper method to fill a column from alternative columns.

        Args:
            index (int): Row index.
            alternatives (List[int]): List of column indices to check.

        Returns:
            str | None: Value found or None.

        Checks each alternative column for a non-empty value and returns the first found.
        """
        result = None
        row = self.df.iloc[index]

        for col_index in alternatives:
            value = row.iloc[col_index]
            if pd.notna(value) and (isinstance(value, str) and value.strip() != ''):
                self.df.iloc[index, col_index] = None
                return str(value).strip()

        return result

    def Filter_by(self, targetColumn: int, column_values: List[str]) -> None:
        """
        Filter the DataFrame by specified column values.

        Args:
            column_values (List[str]): List of column values to filter by.

        (Not implemented yet)
        """
        total_values_found = 0
        results = []

        for _, row in self.df.iterrows():
            
            current_colum_value = str(row[self.original_headers[targetColumn]]).lower() 
            print(current_colum_value)

            for value in column_values:   
                if current_colum_value == value.lower():
                    print(current_colum_value)
                    total_values_found += 1
                    results.append(row)
        
        dataframe = pd.DataFrame(results, columns=self.get_headers())

        if(total_values_found > 0 ):
            echo(style(text=f"{total_values_found} items found.", fg="green", bold=True))
            chose = input("Would you like to set it as current Data? [y/N]: ")
            if(chose == 'y' or chose == 'Y'):
                self.set_current_dataframe(dataframe)
            return
        
        echo(style(text=f"No items found.", fg="red", bold=True))

    def Vicidialize(self, phoneColumn: int, altPhoneColumn: int) -> None:
        """
        Format phone numbers for Vicidial by removing country code (+1), parentheses, dashes, and spaces.

        Args:
            phoneColumn (int): Index of the main phone column.
            altPhoneColumn (int): Index of the alternative phone column.

        For each row, cleans up the phone and alt phone columns.
        """
        for index, row in self.df.iterrows():
            phone = row[self.original_headers[phoneColumn]]
            alt = row[self.original_headers[altPhoneColumn]]

            if not phone:
                echo(style(text=f"No phone on line {index}", fg='red', bold=True))

            if phone:
                self.df.iloc[index, phoneColumn] = self.purge(phone)

            if alt:
                self.df.iloc[index, phoneColumn] = self.purge(alt)

        echo(style(text="Vicidial formatting process completed successfully.", fg="green", bold=True))

    def purge(self, data: str) -> str:
        """
        Clean up a phone number string by removing formatting characters and country code.

        Args:
            data (str): Phone number string.

        Returns:
            str: Cleaned phone number.
        """
        result = ''

        if data:
            if not pd.isna(data):
                result = data.replace("(", "")
                result = result.replace(")", "")
                result = result.replace("-", "")
                result = result.replace(" ", "")
                result = result.strip()
                # US phone numbers should be 10 digits; remove leading digit if 11
                if len(result) == 11:
                    result = result[1:]

        return result
    