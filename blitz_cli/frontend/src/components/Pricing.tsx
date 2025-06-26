import React from 'react';
import { Check, Star, Zap, Building, ArrowRight, Users, Shield, Headphones } from 'lucide-react';

interface PricingProps {
  onSelectPlan: (plan: string) => void;
}

const Pricing: React.FC<PricingProps> = ({ onSelectPlan }) => {
  const plans = [
    {
      name: 'Developer',
      price: '$0',
      period: '/month',
      description: 'Perfect for individual developers and personal projects',
      icon: Zap,
      color: 'primary',
      popular: false,
      features: [
        '10 projects per month',
        'Basic code generation',
        'Community support',
        'Standard frameworks (FastAPI, Node.js, React)',
        'Basic error detection',
        'Terminal CLI access',
        'Public GitHub integration'
      ],
      limitations: [
        'Limited to 10 projects/month',
        'Community support only',
        'Basic templates only'
      ],
      cta: 'Start Free',
      ctaStyle: 'btn-secondary'
    },
    {
      name: 'Professional',
      price: '$19',
      period: '/month',
      description: 'Ideal for professional developers and small teams',
      icon: Star,
      color: 'accent',
      popular: true,
      features: [
        'Unlimited projects',
        'Advanced AI models (GPT-4, Groq, Gemini)',
        'Priority support (24h response)',
        'Custom templates & scaffolding',
        'Team collaboration (up to 5 members)',
        'Advanced debugging & refactoring',
        'Private repository support',
        'Performance optimization',
        'Code review automation',
        'Custom framework support'
      ],
      limitations: [],
      cta: 'Start Pro Trial',
      ctaStyle: 'btn-primary'
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For large teams and organizations with advanced needs',
      icon: Building,
      color: 'success',
      popular: false,
      features: [
        'Everything in Professional',
        'Custom AI model training',
        'SLA guarantee (99.9% uptime)',
        'Dedicated support & success manager',
        'On-premise deployment options',
        'Advanced security & compliance',
        'Custom integrations & APIs',
        'Unlimited team members',
        'Advanced analytics & reporting',
        'Custom training & onboarding'
      ],
      limitations: [],
      cta: 'Contact Sales',
      ctaStyle: 'btn-primary'
    }
  ];

  const colorMap = {
    primary: {
      bg: 'bg-primary-50',
      border: 'border-primary-200',
      text: 'text-primary-600',
      icon: 'text-primary-600'
    },
    accent: {
      bg: 'bg-accent-50',
      border: 'border-accent-200',
      text: 'text-accent-600',
      icon: 'text-accent-600'
    },
    success: {
      bg: 'bg-success-50',
      border: 'border-success-200',
      text: 'text-success-600',
      icon: 'text-success-600'
    }
  };

  return (
    <section id="pricing" className="py-20 gradient-bg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Choose Your <span className="gradient-text">Development Speed</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            From free tier for experimentation to enterprise solutions for large teams. 
            All plans include our core AI-powered code generation.
          </p>
          
          {/* Billing Toggle */}
          <div className="inline-flex items-center bg-white rounded-lg p-1 border border-gray-200">
            <button className="px-4 py-2 text-sm font-medium bg-primary-600 text-white rounded-md">
              Monthly
            </button>
            <button className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900">
              Annual
            </button>
            <div className="ml-2 text-xs bg-accent-100 text-accent-800 px-2 py-1 rounded-full">
              Save 20%
            </div>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => {
            const colors = colorMap[plan.color as keyof typeof colorMap];
            const isPro = plan.popular;
            
            return (
              <div
                key={plan.name}
                className={`
                  relative bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden
                  ${isPro ? 'border-2 border-accent-400 scale-105' : 'border border-gray-200'}
                `}
              >
                {/* Popular Badge */}
                {isPro && (
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                    <div className="bg-gradient-to-r from-accent-500 to-accent-600 text-white px-6 py-2 rounded-full text-sm font-semibold shadow-lg">
                      ⭐ Most Popular
                    </div>
                  </div>
                )}

                <div className="p-8">
                  {/* Header */}
                  <div className="text-center mb-8">
                    <div className={`${colors.bg} ${colors.icon} w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4`}>
                      <plan.icon className="h-8 w-8" />
                    </div>
                    
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">
                      {plan.name}
                    </h3>
                    
                    <p className="text-gray-600 text-sm mb-4">
                      {plan.description}
                    </p>
                    
                    <div className="flex items-baseline justify-center space-x-1">
                      <span className="text-4xl font-bold text-gray-900">
                        {plan.price}
                      </span>
                      <span className="text-gray-500">
                        {plan.period}
                      </span>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="space-y-4 mb-8">
                    {plan.features.map((feature, idx) => (
                      <div key={idx} className="flex items-start space-x-3">
                        <Check className="h-5 w-5 text-success-500 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-700 text-sm">{feature}</span>
                      </div>
                    ))}
                    
                    {/* Limitations for free plan */}
                    {plan.limitations.length > 0 && (
                      <div className="pt-4 border-t border-gray-100">
                        <p className="text-xs text-gray-500 mb-2">Limitations:</p>
                        {plan.limitations.map((limitation, idx) => (
                          <div key={idx} className="flex items-start space-x-3">
                            <div className="w-5 h-5 flex-shrink-0 mt-0.5">
                              <div className="w-2 h-2 bg-gray-300 rounded-full mt-1.5"></div>
                            </div>
                            <span className="text-gray-500 text-xs">{limitation}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* CTA */}
                  <button
                    onClick={() => onSelectPlan(plan.name)}
                    className={`w-full ${plan.ctaStyle} flex items-center justify-center space-x-2 group`}
                  >
                    <span>{plan.cta}</span>
                    <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Features Comparison */}
        <div className="mt-20">
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-8">
            What's Included in Each Plan
          </h3>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center space-y-4">
              <Users className="h-8 w-8 text-primary-600 mx-auto" />
              <h4 className="text-lg font-semibold text-gray-900">Community Support</h4>
              <p className="text-sm text-gray-600">
                Access to our Discord community, documentation, and community-driven support.
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <Headphones className="h-8 w-8 text-accent-600 mx-auto" />
              <h4 className="text-lg font-semibold text-gray-900">Priority Support</h4>
              <p className="text-sm text-gray-600">
                24/7 priority support with guaranteed response times and dedicated assistance.
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <Shield className="h-8 w-8 text-success-600 mx-auto" />
              <h4 className="text-lg font-semibold text-gray-900">Enterprise Security</h4>
              <p className="text-sm text-gray-600">
                Advanced security features, compliance support, and on-premise deployment options.
              </p>
            </div>
          </div>
        </div>

        {/* FAQ */}
        <div className="mt-16 text-center">
          <p className="text-gray-600 mb-4">
            Questions about pricing? We're here to help.
          </p>
          <div className="space-x-4">
            <button className="text-primary-600 hover:text-primary-700 font-medium text-sm">
              View FAQ →
            </button>
            <button className="text-primary-600 hover:text-primary-700 font-medium text-sm">
              Contact Sales →
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Pricing;