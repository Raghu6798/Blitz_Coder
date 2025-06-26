import React, { useState } from 'react';
import { Menu, X, Terminal, Github, LogIn, UserPlus } from 'lucide-react';

interface NavigationProps {
  onSignIn: () => void;
  onSignUp: () => void;
}

const Navigation: React.FC<NavigationProps> = ({ onSignIn, onSignUp }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navItems = [
    { label: 'Home', href: '#home' },
    { label: 'Features', href: '#features' },
    { label: 'Pricing', href: '#pricing' },
    { label: 'Documentation', href: '#docs' },
    { label: 'About', href: '#about' },
    { label: 'Blog', href: '#blog' },
  ];

  return (
    <nav className="bg-white/95 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <Terminal className="h-8 w-8 text-primary-600" />
            <span className="text-xl font-bold gradient-text">BlitzCoder</span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="text-gray-700 hover:text-primary-600 transition-colors duration-200 font-medium"
              >
                {item.label}
              </a>
            ))}
          </div>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center space-x-4">
            <a
              href="https://github.com/blitzcoder"
              className="text-gray-700 hover:text-primary-600 transition-colors duration-200"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github className="h-5 w-5" />
            </a>
            <button
              onClick={onSignIn}
              className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition-colors duration-200 font-medium"
            >
              <LogIn className="h-4 w-4" />
              <span>Sign In</span>
            </button>
            <button
              onClick={onSignUp}
              className="btn-primary flex items-center space-x-2"
            >
              <UserPlus className="h-4 w-4" />
              <span>Get Started Free</span>
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-700 hover:text-primary-600 transition-colors duration-200"
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200 py-4 animate-slide-in">
            <div className="flex flex-col space-y-4">
              {navItems.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className="text-gray-700 hover:text-primary-600 transition-colors duration-200 font-medium px-4 py-2"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.label}
                </a>
              ))}
              <div className="border-t border-gray-200 pt-4 px-4 space-y-3">
                <button
                  onClick={() => {
                    onSignIn();
                    setIsMenuOpen(false);
                  }}
                  className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition-colors duration-200 font-medium w-full"
                >
                  <LogIn className="h-4 w-4" />
                  <span>Sign In</span>
                </button>
                <button
                  onClick={() => {
                    onSignUp();
                    setIsMenuOpen(false);
                  }}
                  className="btn-primary flex items-center space-x-2 w-full justify-center"
                >
                  <UserPlus className="h-4 w-4" />
                  <span>Get Started Free</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;