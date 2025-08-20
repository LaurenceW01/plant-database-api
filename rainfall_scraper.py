#!/usr/bin/env python3
"""
Harris County FWS Rainfall Scraper

This script scrapes rainfall data from the Harris County Flood Warning System
and calculates the total rainfall over the past 7 days for a specified location.

Author: Generated for FWS_Scraper project
"""

import requests
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
from bs4 import BeautifulSoup


class HarrisCountyRainfallScraper:
    """
    A scraper class for extracting rainfall data from Harris County FWS website.
    
    This class handles HTTP requests to the Harris County Flood Warning System
    and processes the returned data to calculate rainfall totals.
    """
    
    def __init__(self, base_url: str = "https://www.harriscountyfws.org"):
        """
        Initialize the scraper with the base URL.
        
        Args:
            base_url (str): The base URL for the Harris County FWS website
        """
        self.base_url = base_url  # Store the base URL for API requests
        self.session = requests.Session()  # Create a persistent session for efficiency
        
        # Set headers to mimic a real browser request
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def construct_url(self, location_id: str, start_date: datetime, span: str = "1 Month") -> str:
        """
        Construct the URL for accessing rainfall data from Harris County FWS.
        
        Args:
            location_id (str): The unique identifier for the monitoring location
            start_date (datetime): The starting date for data retrieval
            span (str): The time span for data (default: "1 Month")
            
        Returns:
            str: The constructed URL for data access
        """
        # Format the date as required by the API (MM/DD/YYYY HH:MM AM/PM)
        formatted_date = start_date.strftime("%m/%d/%Y %I:%M %p")
        # URL encode the date string to handle spaces and special characters
        encoded_date = quote(formatted_date)
        
        # Construct the complete URL with all required parameters
        url = f"{self.base_url}/GageDetail/Index/{location_id}?From={encoded_date}&span={quote(span)}&r=1&v=rainfall&selIdx=1"
        
        return url

    def fetch_page_content(self, url: str) -> Optional[str]:
        """
        Fetch the HTML content of the specified URL.
        
        Args:
            url (str): The URL to fetch content from
            
        Returns:
            Optional[str]: The HTML content if successful, None if failed
        """
        try:
            # Make HTTP GET request to fetch page content
            response = self.session.get(url, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            return response.text  # Return the HTML content as string
            
        except requests.RequestException as e:
            # Log error and return None if request fails
            print(f"Error fetching page content: {e}")
            return None

    def extract_rainfall_data(self, html_content: str) -> Optional[List[Dict]]:
        """
        Extract rainfall data from the HTML content using BeautifulSoup.
        
        The Harris County FWS website displays rainfall data in tables or grids.
        This method looks for various patterns where rainfall data might be stored.
        
        Args:
            html_content (str): The HTML content containing rainfall data
            
        Returns:
            Optional[List[Dict]]: List of rainfall data dictionaries, None if not found
        """
        try:
            # Parse HTML content with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            rainfall_data = []
            
            # Method 1: Look for JSON data embedded in script tags or divs
            json_data = self.extract_json_from_html(html_content)
            if json_data:
                return self.parse_json_rainfall_data(json_data)
            
            # Method 2: Look for DevExpress grid data in table structures
            devex_data = self.extract_devexpress_grid_data(soup)
            if devex_data:
                return devex_data
            
            # Method 3: Look for standard HTML tables with rainfall data
            table_data = self.extract_table_rainfall_data(soup)
            if table_data:
                return table_data
            
            # Method 4: Look for specific text patterns in the HTML
            text_data = self.extract_text_patterns(html_content)
            if text_data:
                return text_data
                
            print("No rainfall data found using any extraction method")
            return None
                
        except Exception as e:
            # Handle any unexpected errors during parsing
            print(f"Error extracting rainfall data: {e}")
            return None

    def extract_json_from_html(self, html_content: str) -> Optional[Dict]:
        """
        Extract JSON data from script tags or hidden elements in HTML.
        
        Args:
            html_content (str): The HTML content to search
            
        Returns:
            Optional[Dict]: Parsed JSON data if found, None otherwise
        """
        try:
            # Look for various JSON patterns in the HTML
            patterns = [
                r'\{"HasData":true.*?"CumulativeGridData":\[.*?\]\}',
                r'\{"rainfall_data":\[.*?\]\}',
                r'\{"SiteId":\d+.*?"DataTime":"[^"]*".*?"DataValue":[^}]*\}',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    return json.loads(json_str)
            
            return None
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error parsing JSON from HTML: {e}")
            return None

    def extract_devexpress_grid_data(self, soup: BeautifulSoup) -> Optional[List[Dict]]:
        """
        Extract data from DevExpress grid controls.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            Optional[List[Dict]]: List of rainfall data if found
        """
        rainfall_data = []
        
        try:
            # Look for DevExpress grid tables
            grid_tables = soup.find_all('table', {'id': re.compile(r'.*GridView.*|.*Grid.*')})
            
            for table in grid_tables:
                # Look for rows with date and rainfall data
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:  # Expect at least date, time, and value columns
                        # Try to extract date and rainfall values
                        text_content = [cell.get_text(strip=True) for cell in cells]
                        
                        # Look for date patterns and numeric values
                        for i, text in enumerate(text_content):
                            if self.is_date_string(text) and i + 2 < len(text_content):
                                # Check if there's a rainfall value nearby
                                for j in range(i, min(i + 3, len(text_content))):
                                    if self.is_rainfall_value(text_content[j]):
                                        rainfall_data.append({
                                            'date': text,
                                            'rainfall': self.clean_rainfall_value(text_content[j])
                                        })
                                        break
            
            return rainfall_data if rainfall_data else None
            
        except Exception as e:
            print(f"Error extracting DevExpress grid data: {e}")
            return None

    def extract_table_rainfall_data(self, soup: BeautifulSoup) -> Optional[List[Dict]]:
        """
        Extract rainfall data from standard HTML tables.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            Optional[List[Dict]]: List of rainfall data if found
        """
        rainfall_data = []
        
        try:
            # Look for tables that might contain rainfall data
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if table headers suggest rainfall data
                headers = table.find_all(['th', 'td'])
                header_text = ' '.join([h.get_text(strip=True).lower() for h in headers[:5]])
                
                if any(keyword in header_text for keyword in ['rain', 'date', 'reading']):
                    rows = table.find_all('tr')[1:]  # Skip header row
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            # Try to find date and rainfall columns
                            date_col = None
                            rain_col = None
                            
                            for i, cell in enumerate(cells):
                                text = cell.get_text(strip=True)
                                if self.is_date_string(text):
                                    date_col = text
                                elif self.is_rainfall_value(text):
                                    rain_col = self.clean_rainfall_value(text)
                            
                            if date_col and rain_col is not None:
                                rainfall_data.append({
                                    'date': date_col,
                                    'rainfall': rain_col
                                })
            
            return rainfall_data if rainfall_data else None
            
        except Exception as e:
            print(f"Error extracting table rainfall data: {e}")
            return None

    def extract_text_patterns(self, html_content: str) -> Optional[List[Dict]]:
        """
        Extract rainfall data using text pattern matching.
        
        Args:
            html_content (str): The HTML content to search
            
        Returns:
            Optional[List[Dict]]: List of rainfall data if found
        """
        rainfall_data = []
        
        try:
            # Look for patterns that indicate rainfall data in text
            patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4})\s+\d{1,2}:\d{2}\s+[AP]M.*?(\d+\.\d+)"?\s*(?:inch|in)',
                r'(\d{1,2}/\d{1,2}/\d{4}).*?(\d+\.\d+)"?\s*(?:inch|in)',
                r'(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}.*?(\d+\.\d+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        date_str, rainfall_str = match
                        try:
                            rainfall_value = float(rainfall_str)
                            rainfall_data.append({
                                'date': date_str,
                                'rainfall': rainfall_value
                            })
                        except ValueError:
                            continue
            
            return rainfall_data if rainfall_data else None
            
        except Exception as e:
            print(f"Error extracting text patterns: {e}")
            return None

    def is_date_string(self, text: str) -> bool:
        """
        Check if a string appears to be a date.
        
        Args:
            text (str): Text to check
            
        Returns:
            bool: True if text looks like a date, False otherwise
        """
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}-\d{1,2}-\d{4}',
        ]
        
        return any(re.match(pattern, text.strip()) for pattern in date_patterns)

    def is_rainfall_value(self, text: str) -> bool:
        """
        Check if a string appears to be a rainfall value.
        
        Args:
            text (str): Text to check
            
        Returns:
            bool: True if text looks like a rainfall value, False otherwise
        """
        try:
            # Remove quotes, inches symbol, and common suffixes
            cleaned = text.strip().strip('"').replace('inches', '').replace('in', '').replace('"', '').strip()
            value = float(cleaned)
            # Reasonable rainfall values (0-50 inches)
            return 0 <= value <= 50
        except (ValueError, AttributeError):
            return False

    def clean_rainfall_value(self, text: str) -> float:
        """
        Clean and convert a rainfall value string to float.
        
        Args:
            text (str): Text containing rainfall value
            
        Returns:
            float: Cleaned rainfall value
        """
        # Remove quotes, inches symbol, and common suffixes
        cleaned = text.strip().strip('"').replace('inches', '').replace('in', '').replace('"', '').strip()
        return float(cleaned)

    def parse_json_rainfall_data(self, json_data: Dict) -> List[Dict]:
        """
        Parse rainfall data from JSON format.
        
        Args:
            json_data (Dict): JSON data containing rainfall information
            
        Returns:
            List[Dict]: List of rainfall data dictionaries
        """
        rainfall_data = []
        
        try:
            # Check if data contains cumulative grid data (from JSON)
            if "CumulativeGridData" in json_data:
                # Process each data point from the cumulative grid
                for data_point in json_data["CumulativeGridData"]:
                    # Extract timestamp and rainfall value from each data point
                    timestamp_str = data_point.get("DataTime", "")
                    rainfall_value = data_point.get("DataValue", 0.0)
                    
                    if timestamp_str:
                        rainfall_data.append({
                            'date': timestamp_str,
                            'rainfall': float(rainfall_value)
                        })
            
            # Check if data contains rainfall table data (from regex extraction)
            elif "rainfall_data" in json_data:
                # Process each rainfall record from table data
                for record in json_data["rainfall_data"]:
                    # Parse start date and rainfall amount
                    start_date_str = record.get("start_date", "")
                    rainfall_amount = record.get("rainfall", 0.0)
                    
                    if start_date_str:
                        rainfall_data.append({
                            'date': start_date_str,
                            'rainfall': float(rainfall_amount)
                        })
            
        except (ValueError, KeyError) as e:
            # Handle parsing errors for date/time or missing keys
            print(f"Error parsing JSON rainfall data: {e}")
        
        return rainfall_data

    def parse_rainfall_data_to_tuples(self, rainfall_data: List[Dict]) -> List[Tuple[datetime, float]]:
        """
        Convert rainfall data from dict format to datetime tuples.
        
        Args:
            rainfall_data (List[Dict]): List of rainfall data dictionaries
            
        Returns:
            List[Tuple[datetime, float]]: List of (datetime, rainfall_amount) tuples
        """
        rainfall_records = []  # Initialize list to store parsed records
        seen_dates = {}  # Dictionary to track unique date/rainfall combinations
        
        try:
            for record in rainfall_data:
                date_str = record.get('date', '')
                rainfall_value = record.get('rainfall', 0.0)
                
                if date_str:
                    # Try different date parsing formats
                    timestamp = None
                    
                    # ISO format with T separator
                    if 'T' in date_str:
                        try:
                            timestamp = datetime.fromisoformat(date_str.replace("T", " ").replace("Z", ""))
                        except ValueError:
                            pass
                    
                    # MM/DD/YYYY format
                    if not timestamp:
                        try:
                            timestamp = datetime.strptime(date_str, "%m/%d/%Y")
                        except ValueError:
                            pass
                    
                    # MM/DD/YYYY HH:MM AM/PM format
                    if not timestamp:
                        try:
                            timestamp = datetime.strptime(date_str, "%m/%d/%Y %I:%M %p")
                        except ValueError:
                            pass
                    
                    # YYYY-MM-DD format
                    if not timestamp:
                        try:
                            timestamp = datetime.strptime(date_str, "%Y-%m-%d")
                        except ValueError:
                            pass
                    
                    if timestamp:
                        # Create a unique key based on date (without time) to deduplicate
                        date_key = timestamp.date()
                        
                        # Only add if we haven't seen this date before, or if this has a higher rainfall value
                        if date_key not in seen_dates or seen_dates[date_key][1] < float(rainfall_value):
                            seen_dates[date_key] = (timestamp, float(rainfall_value))
                    else:
                        print(f"Could not parse date: {date_str}")
            
            # Convert back to list of tuples
            rainfall_records = list(seen_dates.values())
            
        except (ValueError, KeyError) as e:
            # Handle parsing errors for date/time or missing keys
            print(f"Error parsing rainfall data to tuples: {e}")
        
        return rainfall_records  # Return the list of parsed records

    def filter_last_7_days(self, rainfall_data: List[Tuple[datetime, float]]) -> List[Tuple[datetime, float]]:
        """
        Filter rainfall data to include only the 7 complete days prior to today.
        This excludes today's partial data and gets 7 full days of complete readings.
        
        Args:
            rainfall_data (List[Tuple[datetime, float]]): List of (datetime, rainfall) tuples
            
        Returns:
            List[Tuple[datetime, float]]: Filtered data for the 7 complete days prior to today
        """
        # Get today's date (without time)
        today = datetime.now().date()
        
        # Calculate 7 days ago from today (exclusive of today)
        seven_days_ago = today - timedelta(days=7)
        
        # Filter records to include only the 7 complete days prior to today
        # This excludes today's partial data and gets exactly 7 complete days
        filtered_data = [
            (timestamp, rainfall) for timestamp, rainfall in rainfall_data
            if seven_days_ago <= timestamp.date() < today
        ]
        
        return filtered_data

    def calculate_total_rainfall(self, rainfall_data: List[Tuple[datetime, float]]) -> float:
        """
        Calculate the total rainfall from the filtered data.
        
        Args:
            rainfall_data (List[Tuple[datetime, float]]): List of (datetime, rainfall) tuples
            
        Returns:
            float: Total rainfall amount in inches
        """
        # Sum all rainfall values from the filtered data
        total_rainfall = sum(rainfall for _, rainfall in rainfall_data)
        return total_rainfall

    def scrape_rainfall_totals(self, location_id: str = "590") -> Optional[float]:
        """
        Main method to scrape and calculate rainfall totals for the 7 complete days prior to today.
        This excludes today's partial data to ensure accurate 24-hour rainfall measurements.
        
        Args:
            location_id (str): The location ID for the monitoring station (default: "590")
            
        Returns:
            Optional[float]: Total rainfall in inches for the 7 complete days prior to today, None if failed
        """
        try:
            # Use current date as the "From" parameter to get the most recent data
            # The span of "1 Month" will get data from 1 month ago to the current date
            current_date = datetime.now()
            
            # Construct the URL for data retrieval
            url = self.construct_url(location_id, current_date, "1 Month")
            print(f"Fetching data from: {url}")
            
            # Fetch the HTML content from the website
            html_content = self.fetch_page_content(url)
            if not html_content:
                print("Failed to fetch page content")
                return None
            
            # Extract rainfall data from the HTML content using multiple methods
            rainfall_data = self.extract_rainfall_data(html_content)
            if not rainfall_data:
                print("Failed to extract rainfall data")
                return None
            
            # Convert rainfall data to datetime tuples for processing
            rainfall_tuples = self.parse_rainfall_data_to_tuples(rainfall_data)
            if not rainfall_tuples:
                print("No rainfall data could be parsed into datetime format")
                return None
            
            # Filter data to include only the 7 complete days prior to today
            filtered_data = self.filter_last_7_days(rainfall_tuples)
            print(f"Found {len(filtered_data)} rainfall records for the 7 complete days prior to today")
            
            # Calculate and return the total rainfall
            total_rainfall = self.calculate_total_rainfall(filtered_data)
            
            return total_rainfall
            
        except Exception as e:
            # Handle any unexpected errors during the scraping process
            print(f"Error during scraping: {e}")
            return None
    
    def get_current_timestamp(self) -> str:
        """
        Get current timestamp for API responses.
        
        Returns:
            str: Current timestamp in ISO format
        """
        return datetime.now().isoformat()


def main():
    """
    Main function to demonstrate the rainfall scraper functionality.
    
    This function creates a scraper instance and retrieves the 7-day rainfall total
    for the default location (590 - Cole Creek @ Deihl Road).
    """
    # Create an instance of the rainfall scraper
    scraper = HarrisCountyRainfallScraper()
    
    # Define the location ID for Cole Creek @ Deihl Road
    location_id = "590"
    
    print("Harris County FWS Rainfall Scraper")
    print("=" * 40)
    print(f"Fetching rainfall data for location {location_id} (Cole Creek @ Deihl Road)")
    print("Calculating total rainfall for the 7 complete days prior to today...")
    print()
    
    # Scrape the rainfall data and calculate totals
    total_rainfall = scraper.scrape_rainfall_totals(location_id)
    
    # Display the results
    if total_rainfall is not None:
        print(f"Total rainfall for the 7 complete days prior to today: {total_rainfall:.2f} inches")
    else:
        print("Failed to retrieve rainfall data. Please check the connection and try again.")


# Execute the main function when script is run directly
if __name__ == "__main__":
    main()
