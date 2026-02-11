'use client'

import { useRef, useEffect, useState } from 'react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { Play, RotateCcw, Sparkles, Zap, Trophy, Target } from 'lucide-react'
import gsap from 'gsap'
import { 
  useFadeIn, 
  useStaggerFadeIn, 
  useScaleIn,
  animateNumber,
  animateShake,
  animateSuccess
} from '@/lib/animations/gsap-utils'

export default function GSAPDemo() {
  const [activeDemo, setActiveDemo] = useState<string | null>(null)
  
  // Demo refs
  const bounceRef = useRef<HTMLDivElement>(null)
  const spinRef = useRef<HTMLDivElement>(null)
  const morphRef = useRef<HTMLDivElement>(null)
  const numberRef = useRef<HTMLSpanElement>(null)
  const shakeRef = useRef<HTMLDivElement>(null)
  const successRef = useRef<HTMLDivElement>(null)
  const sequenceRef = useRef<HTMLDivElement>(null)
  
  // Page load animations
  const headerRef = useFadeIn(0)
  const cardsRef = useStaggerFadeIn(0.3, 0.1)
  
  const runDemo = (demoName: string) => {
    setActiveDemo(demoName)
    
    switch(demoName) {
      case 'bounce':
        if (bounceRef.current) {
          gsap.fromTo(bounceRef.current,
            { y: 0 },
            { 
              y: -100, 
              duration: 0.5, 
              ease: 'power2.out',
              yoyo: true,
              repeat: 3
            }
          )
        }
        break
        
      case 'spin':
        if (spinRef.current) {
          gsap.to(spinRef.current, {
            rotation: 720,
            scale: 1.5,
            duration: 1,
            ease: 'elastic.out(1, 0.3)'
          })
        }
        break
        
      case 'morph':
        if (morphRef.current) {
          const tl = gsap.timeline()
          tl.to(morphRef.current, {
            borderRadius: '50%',
            backgroundColor: '#8B5CF6',
            scale: 1.2,
            duration: 0.5,
            ease: 'power2.inOut'
          })
          .to(morphRef.current, {
            borderRadius: '10px',
            backgroundColor: '#3B82F6',
            scale: 1,
            duration: 0.5,
            ease: 'power2.inOut'
          })
        }
        break
        
      case 'counter':
        if (numberRef.current) {
          animateNumber(numberRef.current, 0, 9999, 2, 0)
        }
        break
        
      case 'shake':
        if (shakeRef.current) {
          animateShake(shakeRef)
        }
        break
        
      case 'success':
        if (successRef.current) {
          animateSuccess(successRef)
        }
        break
        
      case 'sequence':
        if (sequenceRef.current) {
          const children = Array.from(sequenceRef.current.children)
          const tl = gsap.timeline()
          
          children.forEach((child, index) => {
            tl.fromTo(child,
              { x: -100, opacity: 0, rotation: -180 },
              { 
                x: 0, 
                opacity: 1, 
                rotation: 0,
                duration: 0.5,
                ease: 'back.out(1.7)'
              },
              index * 0.2
            )
          })
        }
        break
    }
    
    setTimeout(() => setActiveDemo(null), 2500)
  }
  
  const resetDemo = (refToReset: React.RefObject<HTMLElement>) => {
    if (refToReset.current) {
      gsap.set(refToReset.current, { clearProps: 'all' })
    }
  }
  
  const resetAllChildren = (containerRef: React.RefObject<HTMLElement>) => {
    if (containerRef.current) {
      const children = containerRef.current.children
      gsap.set(children, { clearProps: 'all' })
    }
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div ref={headerRef}>
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-full mb-4">
            <Sparkles className="w-5 h-5" />
            <span className="font-bold">GSAP Animations Demo</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Interactive Animation Showcase
          </h1>
          <p className="text-gray-600">
            Click the buttons to see GSAP animations in action
          </p>
        </div>
      </div>

      {/* Demo Grid */}
      <div ref={cardsRef} className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Bounce Demo */}
        <Card hover>
          <div className="text-center space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Bounce Effect</h3>
            <div className="h-32 flex items-end justify-center">
              <div
                ref={bounceRef}
                className="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg shadow-lg"
              />
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={() => runDemo('bounce')} 
                disabled={activeDemo === 'bounce'}
                size="sm"
                className="flex-1"
              >
                <Play className="w-4 h-4" />
                Play
              </Button>
              <Button 
                onClick={() => resetDemo(bounceRef)}
                variant="outline"
                size="sm"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>

        {/* Spin Demo */}
        <Card hover>
          <div className="text-center space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Elastic Spin</h3>
            <div className="h-32 flex items-center justify-center">
              <div
                ref={spinRef}
                className="w-16 h-16 bg-gradient-to-br from-purple-400 to-pink-600 rounded-lg shadow-lg flex items-center justify-center"
              >
                <Zap className="w-8 h-8 text-white" />
              </div>
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={() => runDemo('spin')}
                disabled={activeDemo === 'spin'}
                size="sm"
                className="flex-1"
              >
                <Play className="w-4 h-4" />
                Play
              </Button>
              <Button 
                onClick={() => resetDemo(spinRef)}
                variant="outline"
                size="sm"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>

        {/* Morph Demo */}
        <Card hover>
          <div className="text-center space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Shape Morph</h3>
            <div className="h-32 flex items-center justify-center">
              <div
                ref={morphRef}
                className="w-16 h-16 bg-blue-500 rounded-lg shadow-lg"
              />
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={() => runDemo('morph')}
                disabled={activeDemo === 'morph'}
                size="sm"
                className="flex-1"
              >
                <Play className="w-4 h-4" />
                Play
              </Button>
              <Button 
                onClick={() => resetDemo(morphRef)}
                variant="outline"
                size="sm"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>

        {/* Number Counter Demo */}
        <Card hover>
          <div className="text-center space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Number Counter</h3>
            <div className="h-32 flex items-center justify-center">
              <span
                ref={numberRef}
                className="text-5xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent"
              >
                0
              </span>
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={() => runDemo('counter')}
                disabled={activeDemo === 'counter'}
                size="sm"
                className="flex-1"
              >
                <Play className="w-4 h-4" />
                Play
              </Button>
              <Button 
                onClick={() => { if (numberRef.current) numberRef.current.textContent = '0' }}
                variant="outline"
                size="sm"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>

        {/* Shake Demo */}
        <Card hover>
          <div className="text-center space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Shake Alert</h3>
            <div className="h-32 flex items-center justify-center">
              <div
                ref={shakeRef}
                className="px-6 py-3 bg-red-500 text-white font-bold rounded-lg shadow-lg"
              >
                ⚠️ Error!
              </div>
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={() => runDemo('shake')}
                disabled={activeDemo === 'shake'}
                size="sm"
                className="flex-1"
              >
                <Play className="w-4 h-4" />
                Play
              </Button>
              <Button 
                onClick={() => resetDemo(shakeRef)}
                variant="outline"
                size="sm"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>

        {/* Success Demo */}
        <Card hover>
          <div className="text-center space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Success Pop</h3>
            <div className="h-32 flex items-center justify-center">
              <div
                ref={successRef}
                className="w-16 h-16 bg-green-500 rounded-full shadow-lg flex items-center justify-center"
              >
                <Trophy className="w-8 h-8 text-white" />
              </div>
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={() => runDemo('success')}
                disabled={activeDemo === 'success'}
                size="sm"
                className="flex-1"
              >
                <Play className="w-4 h-4" />
                Play
              </Button>
              <Button 
                onClick={() => resetDemo(successRef)}
                variant="outline"
                size="sm"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Sequence Demo */}
      <Card className="bg-gradient-to-br from-indigo-50 to-purple-50">
        <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">
          Staggered Sequence Animation
        </h3>
        <div 
          ref={sequenceRef}
          className="flex flex-wrap gap-4 justify-center mb-6"
        >
          {[1, 2, 3, 4, 5].map((num) => (
            <div
              key={num}
              className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg shadow-lg flex items-center justify-center text-white font-bold text-xl"
            >
              {num}
            </div>
          ))}
        </div>
        <div className="flex gap-2 justify-center">
          <Button 
            onClick={() => runDemo('sequence')}
            disabled={activeDemo === 'sequence'}
          >
            <Play className="w-4 h-4" />
            Play Sequence
          </Button>
          <Button 
            onClick={() => resetAllChildren(sequenceRef)}
            variant="outline"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </Button>
        </div>
      </Card>

      {/* Progress Bar Demo */}
      <Card>
        <h3 className="text-xl font-bold text-gray-900 mb-4">Animated Progress Bars</h3>
        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-600 mb-2 block">Loading Progress</label>
            <ProgressBar percent={75} color="blue" animate={true} />
          </div>
          <div>
            <label className="text-sm text-gray-600 mb-2 block">Success Rate</label>
            <ProgressBar percent={92} color="green" animate={true} />
          </div>
          <div>
            <label className="text-sm text-gray-600 mb-2 block">CPU Usage</label>
            <ProgressBar percent={45} color="yellow" animate={true} />
          </div>
        </div>
      </Card>

      {/* Info Footer */}
      <div className="text-center text-sm text-gray-500 bg-gray-50 rounded-lg p-6">
        <p className="mb-2">
          💡 All animations powered by <strong className="text-gray-900">GSAP</strong>
        </p>
        <p>
          Check out <code className="bg-gray-200 px-2 py-1 rounded">GSAP_ANIMATIONS_GUIDE.md</code> for implementation details
        </p>
      </div>
    </div>
  )
}
