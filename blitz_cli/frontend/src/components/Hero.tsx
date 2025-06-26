import React, { useState, useEffect } from 'react';
import { Play, Github, Star, Users, Terminal, Zap, ArrowRight } from 'lucide-react';

interface HeroProps {
  onGetStarted: () => void;
  onWatchDemo: () => void;
}

const Hero: React.FC<HeroProps> = ({ onGetStarted, onWatchDemo }) => {
  const [typedText, setTypedText] = useState('');
  const [currentStep, setCurrentStep] = useState(0);
  
  const terminalSteps = [
    '$ pip install blitzcoder',
    '$ blitz create ecommerce-api --framework fastapi',
    '✨ Generating project structure...',
    '✅ FastAPI project created successfully!',
    '📁 Files: 23 | Lines: 1,247 | Time: 3.2s'
  ];

  const companies = [
    { name: 'GitHub', logo: '🐙' },
    { name: 'Vercel', logo: '▲' },
    { name: 'Netlify', logo: '◆' },
    { name: 'Supabase', logo: '⚡' },
    { name: 'Railway', logo: '🚂' }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      if (currentStep < terminalSteps.length) {
        const currentCommand = terminalSteps[currentStep];
        if (typedText.length < currentCommand.length) {
          setTypedText(currentCommand.slice(0, typedText.length + 1));
        } else {
          setTimeout(() => {
            setCurrentStep(prev => prev + 1);
            setTypedText('');
          }, 1000);
        }
      } else {
        setCurrentStep(0);
        setTypedText('');
      }
    }, 100);

    return () => clearInterval(timer);
  }, [typedText, currentStep]);

  return (
    <section id="home" className="gradient-bg min-h-screen flex items-center">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="space-y-8 animate-fade-in">
            <div className="space-y-4">
              <h1 className="text-4xl md:text-6xl font-bold text-gray-900 leading-tight">
                Build{' '}
                <span className="gradient-text">Production-Ready</span>{' '}
                Code at{' '}
                <span className="gradient-text">Terminal Speed</span>
              </h1>
              <p className="text-xl text-gray-600 leading-relaxed max-w-2xl">
                AI-powered CLI tool that scaffolds, generates, and optimizes your code projects in seconds. 
                From idea to deployment, faster than ever.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={onGetStarted}
                className="btn-primary flex items-center justify-center space-x-2 text-lg px-8 py-4 group"
              >
                <Zap className="h-5 w-5 group-hover:animate-bounce-subtle" />
                <span>Start Building Now</span>
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={onWatchDemo}
                className="btn-secondary flex items-center justify-center space-x-2 text-lg px-8 py-4 group"
              >
                <Play className="h-5 w-5 group-hover:scale-110 transition-transform" />
                <span>Watch Demo</span>
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="space-y-4">
              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4" />
                  <span className="font-semibold">10,000+</span>
                  <span>developers</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Star className="h-4 w-4 text-yellow-500" />
                  <span className="font-semibold">4.9/5</span>
                  <span>rating</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Github className="h-4 w-4" />
                  <span className="font-semibold">2.3k</span>
                  <span>stars</span>
                </div>
              </div>
              
              {/* Company Logos */}
              <div className="space-y-2">
                <p className="text-sm text-gray-500">Trusted by developers at</p>
                <div className="flex items-center space-x-6">
                  {companies.map((company) => (
                    <div key={company.name} className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors">
                      <span className="text-lg">{company.logo}</span>
                      <span className="font-medium text-sm">{company.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Right Content - Terminal Demo */}
          <div className="relative animate-slide-in">
            <div className="terminal relative overflow-hidden">
              <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-700">
                <div className="flex items-center space-x-2">
                  <Terminal className="h-4 w-4" />
                  <span className="text-xs text-gray-400">BlitzCoder Terminal</span>
                </div>
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
              </div>
              
              <div className="space-y-2 h-64 overflow-hidden">
                {terminalSteps.slice(0, currentStep).map((step, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <span className="text-green-400">$</span>
                    <span className="text-green-400">{step}</span>
                  </div>
                ))}
                {currentStep < terminalSteps.length && (
                  <div className="flex items-start space-x-2">
                    <span className="text-green-400">$</span>
                    <span className="text-green-400">
                      {typedText}
                      <span className="animate-pulse">|</span>
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Floating Elements */}
            <div className="absolute -top-4 -right-4 bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm font-semibold animate-bounce-subtle">
              3.2s ⚡
            </div>
            <div className="absolute -bottom-4 -left-4 bg-success-100 text-success-800 px-3 py-1 rounded-full text-sm font-semibold animate-bounce-subtle delay-300">
              23 files ✨
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;