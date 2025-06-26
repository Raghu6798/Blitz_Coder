import React from 'react';
import { 
  Zap, 
  Brain, 
  Terminal, 
  Search, 
  Shield, 
  Layers,
  ArrowRight,
  Code,
  Cpu,
  FileText
} from 'lucide-react';

const Features: React.FC = () => {
  const features = [
    {
      icon: Layers,
      title: 'Intelligent Project Scaffolding',
      description: 'Generate complete project structures with industry best practices and proper architecture patterns.',
      benefit: 'Skip boilerplate, start building',
      color: 'text-primary-600',
      bgColor: 'bg-primary-100',
      details: ['FastAPI, Node.js, React support', 'Production-ready templates', 'Modular architecture']
    },
    {
      icon: Brain,
      title: 'AI-Powered Code Generation',
      description: 'Production-ready code with proper error handling, documentation, and security implementations.',
      benefit: 'Write less, ship more',
      color: 'text-accent-600',
      bgColor: 'bg-accent-100',
      details: ['Type-safe code', 'Comprehensive documentation', 'Security best practices']
    },
    {
      icon: Code,
      title: 'Multi-Framework Support',
      description: 'Support for FastAPI, Node.js, React, Django, Flask, Express.js and more frameworks.',
      benefit: 'One tool, any stack',
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      details: ['15+ frameworks', 'Language-agnostic', 'Framework-specific optimizations']
    },
    {
      icon: Search,
      title: 'Real-Time Error Detection',
      description: 'Intelligent debugging and automatic code fixes with advanced static analysis.',
      benefit: 'Catch bugs before they catch you',
      color: 'text-error-600',
      bgColor: 'bg-error-100',
      details: ['Static analysis', 'Auto-fix suggestions', 'Performance optimization']
    },
    {
      icon: Terminal,
      title: 'Terminal-Native Experience',
      description: 'Seamless CLI integration that fits perfectly into your existing development workflow.',
      benefit: 'Stay in your flow',
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      details: ['Cross-platform CLI', 'Shell integration', 'Customizable workflows']
    },
    {
      icon: Shield,
      title: 'Enterprise-Grade Security',
      description: 'Secure code generation with privacy-first approach and industry-standard security practices.',
      benefit: 'Your code stays yours',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      details: ['Local processing', 'Encrypted communication', 'SOC 2 compliant']
    }
  ];

  return (
    <section id="features" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Why <span className="gradient-text">BlitzCoder?</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Revolutionary AI-powered development tools that transform how you build, 
            debug, and deploy applications.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className="group bg-white rounded-xl p-8 border border-gray-200 hover:border-primary-300 hover:shadow-xl transition-all duration-300 relative overflow-hidden"
            >
              {/* Background Gradient */}
              <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-gray-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              
              <div className="relative">
                {/* Icon */}
                <div className={`${feature.bgColor} ${feature.color} w-14 h-14 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="h-7 w-7" />
                </div>

                {/* Content */}
                <div className="space-y-4">
                  <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors duration-300">
                    {feature.title}
                  </h3>
                  
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>

                  {/* Benefit Badge */}
                  <div className="inline-flex items-center space-x-2 bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium">
                    <Zap className="h-3 w-3" />
                    <span>{feature.benefit}</span>
                  </div>

                  {/* Details */}
                  <div className="space-y-2 pt-2">
                    {feature.details.map((detail, idx) => (
                      <div key={idx} className="flex items-center space-x-2 text-sm text-gray-500">
                        <ArrowRight className="h-3 w-3 text-primary-400" />
                        <span>{detail}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Hover Effect */}
                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <ArrowRight className={`h-5 w-5 ${feature.color}`} />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <div className="inline-flex items-center space-x-4 bg-gradient-to-r from-primary-50 to-accent-50 px-8 py-4 rounded-lg">
            <Cpu className="h-6 w-6 text-primary-600" />
            <span className="text-gray-700 font-medium">
              Powered by advanced LangGraph AI agents with GPT, Groq, Gemini, and Mistral AI
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;