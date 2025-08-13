#!/usr/bin/env python3
"""
Plant Diagnosis API Test Script

This script demonstrates how to interact with the plant diagnosis API.
It can be used for testing and as a reference for API integration.

Usage:
    python test_diagnosis_api.py <image_path>
    python test_diagnosis_api.py --help
"""

import argparse
import json
import requests
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def diagnose_plant(image_path: str, api_url: str = "http://localhost:5001") -> Optional[Dict[Any, Any]]:
    """
    Send image to plant diagnosis API and return results
    
    Args:
        image_path: Path to the plant image
        api_url: Base URL of the API
        
    Returns:
        Dictionary with diagnosis results or None on failure
    """
    endpoint = f"{api_url}/diagnose/"
    
    # Validate image file exists
    img_file = Path(image_path)
    if not img_file.exists():
        print(f"❌ Error: Image file not found: {image_path}")
        return None
    
    if img_file.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
        print(f"❌ Error: Unsupported image format: {img_file.suffix}")
        return None
    
    print(f"📤 Uploading image: {img_file.name}")
    print(f"🔗 API endpoint: {endpoint}")
    
    try:
        with open(img_file, 'rb') as f:
            files = {'file': (img_file.name, f, f'image/{img_file.suffix[1:]}')}
            
            print("⏳ Processing... (this may take 10-15 seconds)")
            response = requests.post(endpoint, files=files, timeout=30)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else response.text
            print(f"❌ HTTP Error {response.status_code}: {error_detail}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Error: Request timeout (API may be busy)")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to API at {api_url}")
        print("   Make sure the server is running!")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def print_diagnosis_results(result: Dict[Any, Any]) -> None:
    """Pretty print the diagnosis results"""
    
    # Check if it's an error response
    if 'error' in result:
        print("\n❌ Diagnosis Failed")
        print(f"Error: {result['error']}")
        print(f"Message: {result['message']}")
        return
    
    # Success response
    print("\n✅ Diagnosis Complete!")
    print("=" * 50)
    print(f"🌱 Plant Species: {result['plant_name']}")
    print(f"🏥 Health Condition: {result['condition']}")
    print("\n📝 Detailed Diagnosis:")
    print(f"   {result['detail_diagnosis']}")
    
    print("\n📋 Recommended Actions:")
    for action in result['action_plan']:
        print(f"   {action['id']}. {action['action']}")
    
    print("=" * 50)


def test_health_check(api_url: str = "http://localhost:5001") -> bool:
    """Test if the API is healthy and running"""
    try:
        response = requests.get(f"{api_url}/diagnose/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Health: {health_data['status']}")
            return True
        else:
            print(f"❌ API Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach API: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Test the Plant Diagnosis API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python test_diagnosis_api.py my_plant.jpg
    python test_diagnosis_api.py sick_plant.png --url http://localhost:5000
    python test_diagnosis_api.py --health-check
        """
    )
    
    parser.add_argument(
        'image_path',
        nargs='?',
        help='Path to the plant image to diagnose'
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:5001',
        help='API base URL (default: http://localhost:5001)'
    )
    
    parser.add_argument(
        '--health-check',
        action='store_true',
        help='Only check if the API is healthy'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON response'
    )
    
    args = parser.parse_args()
    
    print("🌿 Plant Diagnosis API Test")
    print("=" * 30)
    
    # Health check mode
    if args.health_check:
        is_healthy = test_health_check(args.url)
        sys.exit(0 if is_healthy else 1)
    
    # Validate image path provided
    if not args.image_path:
        print("❌ Error: No image path provided")
        parser.print_help()
        sys.exit(1)
    
    # Test API health first
    if not test_health_check(args.url):
        print("\n💡 Tips:")
        print("   - Make sure the API server is running")
        print("   - Check the API URL is correct")
        print("   - Verify OPENAI_API_KEY is set")
        sys.exit(1)
    
    # Perform diagnosis
    result = diagnose_plant(args.image_path, args.url)
    
    if result is None:
        sys.exit(1)
    
    # Output results
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_diagnosis_results(result)


if __name__ == "__main__":
    main()
