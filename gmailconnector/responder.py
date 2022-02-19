import warnings


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
        self._ok: bool = dictionary.get('ok')
        self._status: int = dictionary.get('status')
        self._body: str = dictionary.get('body')
        self._count: int or None = dictionary.get('count')

    @property
    def ok(self) -> bool:
        """Returns the extracted class variable.

        Returns:
            bool:
            ``True`` or ``False`` based on the arg value received.
        """
        return self._ok

    @property
    def status(self) -> int:
        """Returns the extracted class variable.

        Returns:
            int:
            ``HTTP`` status code as received.
        """
        return self._status

    @property
    def body(self) -> str:
        """Returns the extracted class variable.

        Returns:
            str:
            Returns the message as received.
        """
        return self._body

    def json(self) -> dict:
        """Returns a dictionary of the argument that was received during class initialization.

        Returns:
            dict:
            Returns the dictionary received as arg.
        """
        return self.raw

    @property
    def count(self) -> int:
        """Takes the number of un-read emails and returns it in a class. Only works for read email.

        Returns:
            int:
            Returns the number of unread emails.
        """
        if not isinstance(self._count, int):
            warnings.warn('count property is valid only for the class ReadEmail')
        return self._count
