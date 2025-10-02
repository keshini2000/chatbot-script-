#!/usr/bin/env python3
"""
Quick integration test for the updated Core DNA assistant prompts
"""

import json
from smart_demo_server import generate_intelligent_response

def test_demo_mode_response():
    """Test the demo mode response format"""
    print("🧪 Testing demo mode response format...")
    
    # Mock search results
    mock_results = [
        {
            'title': 'Core DNA E-commerce Platform',
            'url': 'https://coredna.com/features/ecommerce',
            'content': 'Core DNA provides a comprehensive e-commerce platform with advanced features for online stores, including inventory management, payment processing, and customer analytics.',
            'relevance_score': 0.85
        },
        {
            'title': 'Core DNA Integration Capabilities',
            'url': 'https://coredna.com/integrations',
            'content': 'Connect Core DNA with over 100 third-party applications including CRM systems, marketing tools, and payment gateways.',
            'relevance_score': 0.72
        }
    ]
    
    # Test high confidence query
    response = generate_intelligent_response("What is Core DNA?", mock_results)
    
    print("✅ Response structure:")
    print(f"  Text: {response['text'][:100]}...")
    print(f"  Citations: {len(response['citations'])} citations")
    print(f"  Confidence: {response['confidence']}")
    print(f"  Actions: {response['actions']}")
    
    # Validate structure
    assert 'text' in response
    assert 'citations' in response
    assert 'confidence' in response
    assert 'actions' in response
    assert isinstance(response['citations'], list)
    assert isinstance(response['actions'], list)
    
    print("✅ All structure checks passed!")
    
    # Test low confidence scenario
    low_confidence_results = [
        {
            'title': 'Unrelated Content',
            'url': 'https://example.com',
            'content': 'This content is not very relevant to the query.',
            'relevance_score': 0.3
        }
    ]
    
    low_conf_response = generate_intelligent_response("What is quantum computing?", low_confidence_results)
    print(f"\n🔍 Low confidence test:")
    print(f"  Confidence: {low_conf_response['confidence']}")
    print(f"  Action type: {low_conf_response['actions'][0]['type'] if low_conf_response['actions'] else 'none'}")
    
    assert low_conf_response['confidence'] < 0.55
    assert low_conf_response['actions'][0]['type'] == 'clarify'
    
    print("✅ Low confidence handling works correctly!")

if __name__ == "__main__":
    test_demo_mode_response()
    print("\n🎉 All integration tests passed!")