#!/usr/bin/env python3
"""
Demonstrate the differences between old and new Core DNA assistant functionality
"""

from production_server import assemble_grounded_response
import json

def show_old_vs_new_responses():
    """Show side-by-side comparison of old vs new response formats"""
    
    # Mock context data
    context_blocks = [
        {
            'title': 'Core DNA Platform Overview',
            'url': 'https://coredna.com/platform',
            'last_updated': '2024-01-15',
            'excerpt': 'Core DNA is a comprehensive digital commerce platform that enables businesses to create exceptional customer experiences through integrated e-commerce, content management, and customer engagement tools.'
        },
        {
            'title': 'Core DNA Pricing Information',
            'url': 'https://coredna.com/pricing',
            'last_updated': '2024-01-12',
            'excerpt': 'Core DNA offers flexible pricing plans to suit businesses of all sizes. Contact our sales team for custom enterprise solutions and detailed pricing information.'
        }
    ]
    
    test_scenarios = [
        {
            'name': 'HIGH CONFIDENCE - What is Core DNA?',
            'message': 'What is Core DNA?',
            'confidence': 0.85,
            'old_behavior': 'Simple text response without citations or confidence handling'
        },
        {
            'name': 'MEDIUM CONFIDENCE - Tell me about features',
            'message': 'Tell me about features',
            'confidence': 0.65,
            'old_behavior': 'Full response regardless of confidence level'
        },
        {
            'name': 'LOW CONFIDENCE - Random topic',
            'message': 'What about quantum mechanics?',
            'confidence': 0.35,
            'old_behavior': 'Generic fallback message, no clarification'
        },
        {
            'name': 'LEAD CAPTURE - Demo request',
            'message': 'I need a demo and pricing information',
            'confidence': 0.80,
            'old_behavior': 'Standard response, no lead capture logic'
        }
    ]
    
    print("📊 CORE DNA ASSISTANT - OLD vs NEW COMPARISON")
    print("=" * 80)
    
    for scenario in test_scenarios:
        print(f"\n🎯 SCENARIO: {scenario['name']}")
        print(f"   Message: '{scenario['message']}'")
        print(f"   Confidence: {scenario['confidence']}")
        print()
        
        # Show old behavior
        print("❌ OLD BEHAVIOR:")
        print(f"   {scenario['old_behavior']}")
        print()
        
        # Show new behavior
        print("✅ NEW BEHAVIOR:")
        new_response = assemble_grounded_response(scenario['message'], context_blocks, scenario['confidence'])
        
        print(f"   Response Type: Structured JSON")
        print(f"   Text Length: {len(new_response['text'])} chars")
        print(f"   Citations: {len(new_response['citations'])} sources")
        print(f"   Confidence: {new_response['confidence']}")
        print(f"   Action Type: {new_response['actions'][0]['type']}")
        
        if new_response['actions'][0]['type'] == 'collect_lead':
            print(f"   Lead Fields: {new_response['actions'][0].get('fields', [])}")
        
        print(f"\n   📝 Response Preview:")
        print(f"   \"{new_response['text'][:100]}...\"")
        
        if new_response['citations']:
            print(f"\n   📚 Citations:")
            for i, citation in enumerate(new_response['citations'][:2]):
                print(f"   [{i+1}] {citation['title']} → {citation['url']}")
        
        print("\n" + "-" * 80)

def show_json_output_example():
    """Show actual JSON output example"""
    print("\n📄 EXAMPLE STRICT JSON OUTPUT")
    print("=" * 50)
    
    context = [{
        'title': 'Core DNA E-commerce Features',
        'url': 'https://coredna.com/features/ecommerce',
        'last_updated': '2024-01-15',
        'excerpt': 'Our e-commerce platform includes inventory management, payment processing, order tracking, and comprehensive analytics dashboards for business insights.'
    }]
    
    response = assemble_grounded_response("What e-commerce features does Core DNA have?", context, 0.9)
    
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    show_old_vs_new_responses()
    show_json_output_example()