'use client';

import { useEffect } from 'react';

export default function CoreDNADemo() {
  // Load the chatbot widget
  useEffect(() => {
    const script = document.createElement('script');
    script.src = '/coredna-chatbot.js';
    script.async = true;
    document.body.appendChild(script);

    return () => {
      // Cleanup: remove the widget when component unmounts
      const widget = document.getElementById('coredna-chatbot-widget');
      if (widget) {
        widget.remove();
      }
      // Remove script
      document.body.removeChild(script);
    };
  }, []);
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation - Faithful to Core DNA design */}
      <nav className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl font-bold text-black">Core</span>
                <span className="text-2xl font-bold text-red-600 ml-1">dna</span>
              </div>
            </div>

            {/* Navigation Menu - Simplified for demo */}
            <div className="hidden lg:block">
              <div className="flex space-x-8">
                <div className="relative group">
                  <button className="text-gray-900 hover:text-red-600 px-3 py-2 text-sm font-medium transition-colors">
                    Platform
                  </button>
                </div>
                <div className="relative group">
                  <button className="text-gray-900 hover:text-red-600 px-3 py-2 text-sm font-medium transition-colors">
                    Solutions
                  </button>
                </div>
                <div className="relative group">
                  <button className="text-gray-900 hover:text-red-600 px-3 py-2 text-sm font-medium transition-colors">
                    Resources
                  </button>
                </div>
                <div className="relative group">
                  <button className="text-gray-900 hover:text-red-600 px-3 py-2 text-sm font-medium transition-colors">
                    Why Core dna
                  </button>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex items-center space-x-4">
              <button className="text-gray-900 hover:text-red-600 px-3 py-2 text-sm font-medium transition-colors">
                Login
              </button>
              <button className="bg-red-600 text-white px-6 py-2 rounded-sm text-sm font-medium hover:bg-red-700 transition-colors">
                Watch a demo
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section - Core DNA Style */}
      <section className="bg-white pt-20 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl lg:text-6xl font-bold text-black leading-tight mb-6">
                AUTOMATE.<br />
                ORCHESTRATE.<br />
                <span className="text-red-600">ACCELERATE</span>
              </h1>
              <p className="text-xl text-gray-700 mb-8 leading-relaxed">
                Core dna is a Digital Experience Platform (DXP) that empowers businesses to build, 
                manage, and scale their digital experiences across all channels.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button className="bg-red-600 text-white px-8 py-4 rounded-sm text-lg font-medium hover:bg-red-700 transition-colors">
                  Book a personalized walkthrough
                </button>
                <button className="border-2 border-gray-300 text-gray-900 px-8 py-4 rounded-sm text-lg font-medium hover:border-gray-400 transition-colors">
                  Why Core dna
                </button>
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg h-96 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-4">🚀</div>
                  <p className="text-gray-600 font-medium">Digital Experience Platform</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-black mb-6">
              A platform that grows with your business
            </h2>
            <p className="text-xl text-gray-700 max-w-3xl mx-auto">
              From content management to ecommerce and beyond, Core dna provides all the tools 
              you need to create exceptional digital experiences.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-lg shadow-sm">
              <div className="text-4xl mb-4">🛒</div>
              <h3 className="text-2xl font-bold text-black mb-4">Ecommerce</h3>
              <p className="text-gray-700">
                Complete ecommerce platform with advanced merchandising, 
                flexible pricing, and seamless integrations.
              </p>
            </div>

            <div className="bg-white p-8 rounded-lg shadow-sm">
              <div className="text-4xl mb-4">📝</div>
              <h3 className="text-2xl font-bold text-black mb-4">Content Management</h3>
              <p className="text-gray-700">
                Intuitive CMS with powerful workflow tools, version control, 
                and multi-channel publishing capabilities.
              </p>
            </div>

            <div className="bg-white p-8 rounded-lg shadow-sm">
              <div className="text-4xl mb-4">🔗</div>
              <h3 className="text-2xl font-bold text-black mb-4">API & Integrations</h3>
              <p className="text-gray-700">
                Flexible API architecture with pre-built integrations to 
                connect your entire tech stack seamlessly.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial/Case Study Section */}
      <section className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-black mb-6">
                Built for complexity,<br />
                designed for simplicity
              </h2>
              <p className="text-xl text-gray-700 mb-8">
                Whether you're a growing startup or an enterprise organization, 
                Core dna adapts to your unique business requirements and scales with your growth.
              </p>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="text-gray-700">Flexible architecture that adapts to your business model</p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="text-gray-700">Scalable infrastructure for high-performance applications</p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="text-gray-700">Enterprise-grade security and compliance features</p>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-50 to-red-50 rounded-lg h-96 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-4">⚡</div>
                  <p className="text-gray-600 font-medium">Performance & Scale</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-black py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to accelerate your digital transformation?
          </h2>
          <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
            Join hundreds of businesses already using Core dna to deliver 
            exceptional digital experiences at scale.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-red-600 text-white px-8 py-4 rounded-sm text-lg font-medium hover:bg-red-700 transition-colors">
              Book a personalized walkthrough
            </button>
            <button className="border-2 border-white text-white px-8 py-4 rounded-sm text-lg font-medium hover:bg-white hover:text-black transition-colors">
              Watch a demo
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <span className="text-2xl font-bold text-white">Core</span>
                <span className="text-2xl font-bold text-red-600 ml-1">dna</span>
              </div>
              <p className="text-gray-400 text-sm">
                The Digital Experience Platform that empowers businesses to 
                automate, orchestrate, and accelerate their digital transformation.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Platform</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Content Management</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Ecommerce</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API & Integrations</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Analytics</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Solutions</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Enterprise</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Mid-Market</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Startups</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Agencies</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
            <p>&copy; 2025 Core dna. All rights reserved.</p>
            <p className="mt-2 text-xs">
              🤖 <strong>Demo Site</strong> - This is a demonstration of the Core DNA chatbot integration. 
              Try the chat widget in the bottom-right corner!
            </p>
          </div>
        </div>
      </footer>

    </div>
  );
}