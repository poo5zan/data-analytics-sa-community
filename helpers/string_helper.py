"""Helper methods for string"""


class StringHelper:
    """string helper methods"""

    def is_null_or_whitespace(self, input_str: str):
        """Check if the input string is null or whitespace"""
        return not input_str or str(input_str).isspace()

    def validate_null_or_empty(self, input_str: str, param_name: str):
        """
        Validate null or empty
        """
        if self.is_null_or_whitespace(param_name):
            raise ValueError("Param name is required")

        if self.is_null_or_whitespace(input_str):
            raise ValueError(f"{param_name} is null or empty")
