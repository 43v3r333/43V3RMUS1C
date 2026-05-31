import Link from 'next/link'

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight">43V3R CORE</h1>
        <p className="mt-2 text-muted-foreground">
          Enterprise-Grade Autonomous Media Operating System
        </p>
        <div className="mt-8 flex gap-4 justify-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Enter Dashboard
          </Link>
        </div>
      </div>
    </main>
  )
}