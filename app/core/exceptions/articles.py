from fastapi import HTTPException, status


class FailedParsingException(HTTPException):
    def __init__(self, url: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse article: {url}",
        )


class ArticleNotFoundException(HTTPException):
    def __init__(self, url: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with URL {url} not found",
        )


class SummaryNotFoundException(HTTPException):
    def __init__(self, url: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Summary for article {url} not found",
        )


class FailedGeneratingSummaryException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary for article",
        )
