from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
import requests

from app.models.book import BookModel


router = APIRouter()
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
api_key = ""


@router.get("/books/", response_model=List[BookModel])
def get_books(query: str, max_results: int = 10):
    # Example: http://127.0.0.1:8000/api/books/?query=harry&max_results=1
    url = (
        f"https://www.googleapis.com/books/v1/volumes?"
        f"q={requests.utils.quote(query)}&maxResults={max_results}&key={api_key}"
    )
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Error fetching books from Google API"
        )

    data = response.json()

    books = []
    for item in data.get("items", []):
        book_data = {
            "google_books_id": item["id"],
            "volumeInfo": item.get("volumeInfo", {}),
            "saleInfo": item.get("saleInfo"),
            "accessInfo": item.get("accessInfo", {}),
        }

        try:
            books.append(BookModel(**book_data))
        except ValidationError as e:
            print(f"Error in Book model creation: {e}")
            return None
    return books


# {'kind': 'books#volumes', 'totalItems': 2487, 'items': [{'kind': 'books#volume', 'id': 'Hoz-EAAAQBAJ', 'etag': '8Se408BluNc', 'selfLink': 'https://www.googleapis.com/books/v1/volumes/Hoz-EAAAQBAJ', 'volumeInfo': {'title': 'Meghan and Harry', 'subtitle': 'The Real Story: Persecutors or Victims', 'authors': ['Lady Colin Campbell'], 'publisher': 'Simon and Schuster', 'publishedDate': '2024-04-16', 'description': '**A Wall Street Journal bestseller** An updated edition of this blockbuster narrative provides the first behind-the-scenes, authoritative account of the Duke and Duchess of Sussex’s marriage, by the New York Times bestselling author of Diana in Private. The fall from popular grace of Prince Harry, the previously adulated brother of the heir to the British throne, as a consequence of his marriage to the beautiful and dynamic Hollywood actress and "Suits star" Meghan Markle, makes for fascinating reading in this groundbreaking book from Lady Colin Campbell, who is the New York Times bestselling biographer of books on Princess Diana, the Queen Mother, and Queen Elizabeth’s marriage. With a unique breadth of insight, Lady Colin Campbell goes behind the scenes, speaking to friends, relations, courtiers, and colleagues on both sides of the Atlantic to reveal the most unexpected royal story since King Edward VIII\'s abdication. She highlights the dilemmas involved and the issues that lurk beneath the surface, revealing why the couple decided to step down as senior royals. She analyses the implications of the actions of a young and ambitious Duke and Duchess of Sussex, in love with each other and with the empowering lure of fame and fortune, and leads the reader through the maze of contradictions Meghan and Harry have created—while also evoking the Californian culture that has influenced the couple\'s conduct. Meghan and Harry: The Real Story exposes how the royal couple tried and failed to change the royal system—by adapting it to their own needs and ambitions—and, upon failing, how they decided to create a new system—and life—for themselves.', 'industryIdentifiers': [{'type': 'ISBN_13', 'identifier': '9781639367948'}, {'type': 'ISBN_10', 'identifier': '1639367942'}], 'readingModes': {'text': True, 'image': False}, 'pageCount': 581, 'printType': 'BOOK', 'categories': ['Biography & Autobiography'], 'maturityRating': 'NOT_MATURE', 'allowAnonLogging': True, 'contentVersion': '1.2.2.0.preview.2', 'panelizationSummary': {'containsEpubBubbles': False, 'containsImageBubbles': False}, 'imageLinks': {'smallThumbnail': 'http://books.google.com/books/content?id=Hoz-EAAAQBAJ&printsec=frontcover&img=1&zoom=5&edge=curl&source=gbs_api', 'thumbnail': 'http://books.google.com/books/content?id=Hoz-EAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api'}, 'language': 'en', 'previewLink': 'http://books.google.com/books?id=Hoz-EAAAQBAJ&printsec=frontcover&dq=harry&hl=&cd=1&source=gbs_api', 'infoLink': 'https://play.google.com/store/books/details?id=Hoz-EAAAQBAJ&source=gbs_api', 'canonicalVolumeLink': 'https://play.google.com/store/books/details?id=Hoz-EAAAQBAJ'}, 'saleInfo': {'country': 'US', 'saleability': 'FOR_SALE', 'isEbook': True, 'listPrice': {'amount': 12.99, 'currencyCode': 'USD'}, 'retailPrice': {'amount': 12.99, 'currencyCode': 'USD'}, 'buyLink': 'https://play.google.com/store/books/details?id=Hoz-EAAAQBAJ&rdid=book-Hoz-EAAAQBAJ&rdot=1&source=gbs_api', 'offers': [{'finskyOfferType': 1, 'listPrice': {'amountInMicros': 12990000, 'currencyCode': 'USD'}, 'retailPrice': {'amountInMicros': 12990000, 'currencyCode': 'USD'}, 'giftable': True}]}, 'accessInfo': {'country': 'US', 'viewability': 'PARTIAL', 'embeddable': True, 'publicDomain': False, 'textToSpeechPermission': 'ALLOWED_FOR_ACCESSIBILITY', 'epub': {'isAvailable': True, 'acsTokenLink': 'http://books.google.com/books/download/Meghan_and_Harry-sample-epub.acsm?id=Hoz-EAAAQBAJ&format=epub&output=acs4_fulfillment_token&dl_type=sample&source=gbs_api'}, 'pdf': {'isAvailable': False}, 'webReaderLink': 'http://play.google.com/books/reader?id=Hoz-EAAAQBAJ&hl=&source=gbs_api', 'accessViewStatus': 'SAMPLE', 'quoteSharingAllowed': False}, 'searchInfo': {'textSnippet': 'A Wall Street Journal bestseller Meghan and Harry: The Real Story: Persecutors or Victims presents the reader with a strikingly forthright analysis of what happens when a vulnerable male, raised in the traditions of the Old World and ...'}}]}
