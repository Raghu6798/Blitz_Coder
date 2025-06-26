import React from 'react';
import { Download, MessageSquare, Rocket, ArrowRight, Terminal, Code, Reply as Deploy } from 'lucide-react';

const HowItWorks: React.FC = () => {
  const steps = [
    {
      step: '01',
      icon: Download,
      title: 'Install & Configure',
      description: 'Quick installation with npm and seamless setup in your terminal environment.',
      command: 'npm install -g blitzcoder',
      details: ['Cross-platform support', 'Zero configuration needed', 'Integrates with existing tools'],
      color: 'primary'
    },
    {
      step: '02',
      icon: MessageSquare,
      title: 'Describe Your Project',
      description: 'Simply tell BlitzCoder what you want to build using natural language commands.',
      command: 'blitz create ecommerce-api --framework fastapi',
      details: ['Natural language interface', 'Framework-specific templates', 'Intelligent project analysis'],
      color: 'accent'
    },
    {
      step: '03',
      icon: Rocket,
      title: 'Build & Deploy',
      description: 'Get complete, production-ready code with tests, documentation, and deployment configs.',
      command: '✨ Complete project ready in 3.2 seconds',
      details: ['Production-ready code', 'Comprehensive testing', 'Deployment configurations'],
      color: 'success'
    }
  ];

  const colorMap = {
    primary: {
      bg: 'bg-primary-100',
      text: 'text-primary-600',
      border: 'border-primary-200',
      gradient: 'from-primary-500 to-primary-600'
    },
    accent: {
      bg: 'bg-accent-100',
      text: 'text-accent-600',
      border: 'border-accent-200',
      gradient: 'from-accent-500 to-accent-600'
    },
    success: {
      bg: 'bg-success-100',
      text: 'text-success-600',
      border: 'border-success-200',
      gradient: 'from-success-500 to-success-600'
    }
  };

  return (
    <section id="how-it-works" className="py-20 gradient-bg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            How <span className="gradient-text">BlitzCoder</span> Works
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            From installation to deployment in three simple steps. 
            Experience the fastest way to build production-ready applications.
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connection Lines */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-200 via-accent-200 to-success-200 transform -translate-y-1/2 z-0"></div>
          
          <div className="grid lg:grid-cols-3 gap-8 lg:gap-12 relative z-10">
            {steps.map((step, index) => {
              const colors = colorMap[step.color as keyof typeof colorMap];
              
              return (
                <div key={step.step} className="relative group">
                  {/* Step Card */}
                  <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden border border-gray-100">
                    {/* Background Gradient */}
                    <div className={`absolute inset-0 bg-gradient-to-br ${colors.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
                    
                    <div className="relative">
                      {/* Step Number */}
                      <div className="flex items-center justify-between mb-6">
                        <div className={`${colors.bg} ${colors.text} w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg`}>
                          {step.step}
                        </div>
                        <div className={`${colors.bg} ${colors.text} p-3 rounded-lg group-hover:scale-110 transition-transform duration-300`}>
                          <step.icon className="h-6 w-6" />
                        </div>
                      </div>

                      {/* Content */}
                      <div className="space-y-4">
                        <h3 className="text-xl font-bold text-gray-900">
                          {step.title}
                        </h3>
                        
                        <p className="text-gray-600 leading-relaxed">
                          {step.description}
                        </p>

                        {/* Terminal Command */}
                        <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm relative overflow-hidden">
                          <div className="flex items-center space-x-2">
                            <Terminal className="h-4 w-4" />
                            <span className="text-xs text-gray-400">Terminal</span>
                          </div>
                          <div className="mt-2">
                            <span className="text-green-400">$ </span>
                            <span>{step.command}</span>
                          </div>
                          {/* Animated cursor */}
                          <div className="absolute bottom-4 right-4 w-2 h-4 bg-green-400 animate-pulse"></div>
                        </div>

                        {/* Details */}
                        <div className="space-y-2">
                          {step.details.map((detail, idx) => (
                            <div key={idx} className="flex items-center space-x-2 text-sm text-gray-500">
                              <ArrowRight className={`h-3 w-3 ${colors.text}`} />
                              <span>{detail}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Arrow for large screens */}
                  {index < steps.length - 1 && (
                    <div className="hidden lg:block absolute top-1/2 -right-6 transform -translate-y-1/2 z-20">
                      <div className="bg-white rounded-full p-2 shadow-lg">
                        <ArrowRight className="h-4 w-4 text-gray-400" />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom Stats */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div className="space-y-2">
            <div className="text-3xl font-bold text-primary-600">3.2s</div>
            <div className="text-sm text-gray-600">Average generation time</div>
          </div>
          <div className="space-y-2">
            <div className="text-3xl font-bold text-accent-600">15+</div>
            <div className="text-sm text-gray-600">Supported frameworks</div>
          </div>
          <div className="space-y-2">
            <div className="text-3xl font-bold text-success-600">99.9%</div>
            <div className="text-sm text-gray-600">Code accuracy</div>
          </div>
          <div className="space-y-2">
            <div className="text-3xl font-bold text-purple-600">85%</div>
            <div className="text-sm text-gray-600">Time saved</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;