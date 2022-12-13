from typing import Any


class Response:
    """Class to format the response, so that it can be accessed as an object variable.

    >>> Response

    """

    def __init__(self, dictionary: dict):
        """Extracts the properties ``ok``, ``status`` and ``body`` from a dictionary.

        Args:
            dictionary: Takes a dictionary of key-value pairs as an argument.
        """
        self.raw: dict = dictionary

    @property
    def ok(self) -> bool:
        """Returns the extracted class variable.

        Returns:
            bool:
            ``True`` or ``False`` based on the arg value received.
        """
        return self.raw.get('ok')

    @property
    def status(self) -> int:
        """Returns the extracted class variable.

        Returns:
            int:
            ``HTTP`` status code as received.
        """
        return self.raw.get('status')

    @property
    def body(self) -> str:
        """Returns the extracted class variable.

        Returns:
            str:
            Returns the message as received.
        """
        return self.raw.get('body')

    def json(self) -> dict:
        """Returns a dictionary of the argument that was received during class initialization.

        Returns:
            dict:
            Returns the dictionary received as arg.
        """
        return self.raw

    @property
    def count(self) -> int:
        """Takes the number of un-read emails and returns it in a class.

        Returns:
            int:
            Returns the number of unread emails.
        """
        return self.raw.get('count')

    @property
    def extra(self) -> Any:
        """Returns the extra information as a member of the class.

        Returns:
            Any:
            Returns information as received.
        """
        return self.raw.get('extra')
