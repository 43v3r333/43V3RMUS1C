import { Metadata } from 'next'
import KnowledgeGraphWorkspace from '@/components/cognitive/KnowledgeGraphWorkspace'

export const metadata: Metadata = {
  title: 'Knowledge Graph | 43V3R CORE',
  description: 'Semantic orchestration memory explorer',
}

export default function GraphPage() {
  return <KnowledgeGraphWorkspace />
}