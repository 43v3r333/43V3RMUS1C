import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Settings | 43V3R CORE',
  description: 'Account and preferences',
}

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Manage your account and preferences
        </p>
      </div>

      {/* Settings Sections */}
      <div className="space-y-6">
        {/* Profile */}
        <div className="rounded-lg border border-border bg-card">
          <div className="border-b border-border p-4">
            <h2 className="font-medium">Profile</h2>
          </div>
          <div className="p-4 space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="text-sm text-muted-foreground">First Name</label>
                <input
                  type="text"
                  className="mt-1 h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                  placeholder="First name"
                />
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Last Name</label>
                <input
                  type="text"
                  className="mt-1 h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                  placeholder="Last name"
                />
              </div>
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Email</label>
              <input
                type="email"
                className="mt-1 h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                placeholder="email@example.com"
              />
            </div>
          </div>
        </div>

        {/* Security */}
        <div className="rounded-lg border border-border bg-card">
          <div className="border-b border-border p-4">
            <h2 className="font-medium">Security</h2>
          </div>
          <div className="p-4 space-y-4">
            <button className="inline-flex items-center gap-2 rounded-md border border-input bg-background px-4 py-2 text-sm hover:bg-accent">
              Change Password
            </button>
            <button className="inline-flex items-center gap-2 rounded-md border border-input bg-background px-4 py-2 text-sm hover:bg-accent">
              Enable 2FA
            </button>
          </div>
        </div>

        {/* Notifications */}
        <div className="rounded-lg border border-border bg-card">
          <div className="border-b border-border p-4">
            <h2 className="font-medium">Notifications</h2>
          </div>
          <div className="p-4 space-y-4">
            {[
              { label: 'Email notifications', enabled: true },
              { label: 'Render completion alerts', enabled: true },
              { label: 'Social media mentions', enabled: false },
              { label: 'Weekly digest', enabled: true },
            ].map((setting, i) => (
              <div key={i} className="flex items-center justify-between">
                <span className="text-sm">{setting.label}</span>
                <button className={`relative h-5 w-9 rounded-full transition-colors ${
                  setting.enabled ? 'bg-primary' : 'bg-muted'
                }`}>
                  <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-transform ${
                    setting.enabled ? 'left-4.5' : 'left-0.5'
                  }`} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}