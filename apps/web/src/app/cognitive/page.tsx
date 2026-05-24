"""
Cognitive Operating Center Page
"""
import { Metadata } from 'next'
import CognitiveOperatingCenter from '@/components/cognitive/CognitiveOperatingCenter'

export const metadata: Metadata = {
  title: 'Cognitive Operating Center | 43V3R CORE',
  description: 'Real-time orchestration intelligence dashboard',
}

export default function CognitivePage() {
  return <CognitiveOperatingCenter />
}