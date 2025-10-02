#!/usr/bin/env python3
"""
Test the strict JSON output format for Core DNA assistant
"""

import json
from production_server import assemble_grounded_response as prod_assembler
from smart_demo_server import assemble_grounded_response as demo_assembler

def test_strict_json_format():
    """Test that both assemblers return proper strict JSON format"""
    
    # Mock context blocks
    context_blocks = [
        {
            'title': 'Core DNA E-commerce Platform',
            'url': 'https://coredna.com/features/ecommerce',
            'last_updated': '2024-01-15',
            'excerpt': 'Core DNA provides a comprehensive e-commerce platform with advanced features for online stores, including inventory management, payment processing, and customer analytics.'
        },
        {
            'title': 'Core DNA Integration Capabilities',
            'url': 'https://coredna.com/integrations',
            'last_updated': '2024-01-10',
            'excerpt': 'Connect Core DNA with over 100 third-party applications including CRM systems, marketing tools, and payment gateways.'
        }
    ]
    
    test_cases = [
        {
            'name': 'High confidence query',
            'message': 'What is Core DNA?',
            'confidence': 0.85
        },
        {
            'name': 'Medium confidence query',
            'message': 'Tell me about features',
            'confidence': 0.65
        },
        {
            'name': 'Low confidence query',
            'message': 'What about quantum computing?',
            'confidence': 0.35
        },
        {
            'name': 'Lead capture trigger',
            'message': 'I need a demo and pricing information',
            'confidence': 0.80
        }
    ]
    
    print("🧪 Testing Strict JSON Output Format")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n📋 Test Case: {test_case['name']}")
        print(f"   Message: '{test_case['message']}'")
        print(f"   Confidence: {test_case['confidence']}")
        
        # Test production assembler
        print("\n🏭 Production Server Response:")
        prod_response = prod_assembler(test_case['message'], context_blocks, test_case['confidence'])
        print(f"   Type: {type(prod_response)}")
        
        # Validate JSON structure
        validate_json_structure(prod_response, "Production")
        
        # Test demo assembler  
        print("\n🎮 Demo Server Response:")
        demo_response = demo_assembler(test_case['message'], context_blocks, test_case['confidence'])
        print(f"   Type: {type(demo_response)}")
        
        # Validate JSON structure
        validate_json_structure(demo_response, "Demo")
        
        # Test JSON serialization
        try:
            prod_json = json.dumps(prod_response)
            demo_json = json.dumps(demo_response)
            print("   ✅ JSON serialization successful")
        except Exception as e:
            print(f"   ❌ JSON serialization failed: {e}")
        
        print("-" * 30)

def validate_json_structure(response, server_type):
    """Validate the JSON response structure"""
    required_fields = ['text', 'citations', 'confidence', 'actions']
    
    print(f"   {server_type} JSON Structure:")
    
    # Check required fields
    for field in required_fields:
        if field in response:
            print(f"     ✅ {field}: {type(response[field])}")
        else:
            print(f"     ❌ Missing field: {field}")
    
    # Validate field types
    if 'text' in response and isinstance(response['text'], str):
        print(f"     📝 Text length: {len(response['text'])} chars")
        if response['text'].endswith('?'):
            print("     ❓ Ends with question mark (clarifying question)")
    
    if 'citations' in response and isinstance(response['citations'], list):
        print(f"     📚 Citations count: {len(response['citations'])}")
        for i, citation in enumerate(response['citations']):
            if isinstance(citation, dict):
                citation_fields = ['title', 'url', 'quote']
                missing = [f for f in citation_fields if f not in citation]
                if missing:
                    print(f"       ❌ Citation {i} missing: {missing}")
                else:
                    print(f"       ✅ Citation {i} complete")
    
    if 'confidence' in response:
        conf = response['confidence']
        if isinstance(conf, (int, float)) and 0 <= conf <= 1:
            print(f"     📊 Confidence: {conf:.3f} (valid range)")
        else:
            print(f"     ❌ Invalid confidence: {conf}")
    
    if 'actions' in response and isinstance(response['actions'], list):
        print(f"     🎯 Actions count: {len(response['actions'])}")
        for i, action in enumerate(response['actions']):
            if isinstance(action, dict) and 'type' in action:
                action_type = action['type']
                valid_types = ['none', 'clarify', 'handoff', 'collect_lead', 'use_tool']
                if action_type in valid_types:
                    print(f"       ✅ Action {i}: {action_type}")
                    if action_type == 'collect_lead' and 'fields' in action:
                        print(f"         📋 Lead fields: {action['fields']}")
                else:
                    print(f"       ❌ Invalid action type: {action_type}")

def test_edge_cases():
    """Test edge cases and error conditions"""
    print("\n🔧 Testing Edge Cases")
    print("=" * 30)
    
    # Empty context blocks
    print("\n📋 Empty Context Blocks:")
    empty_response = demo_assembler("What is Core DNA?", [], 0.5)
    validate_json_structure(empty_response, "Demo")
    
    # Very low confidence
    print("\n📋 Very Low Confidence:")
    low_conf_response = prod_assembler("Random query", [], 0.1)
    validate_json_structure(low_conf_response, "Production")

if __name__ == "__main__":
    test_strict_json_format()
    test_edge_cases()
    print("\n🎉 All strict JSON format tests completed!")