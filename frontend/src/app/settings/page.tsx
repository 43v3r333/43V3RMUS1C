"""
Settings page
*/
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import {
  User,
  Lock,
  Bell,
  Palette,
  Globe,
  Shield,
  Key,
  Mail,
  Smartphone,
} from "lucide-react"

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Manage your account and preferences
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="appearance">Appearance</TabsTrigger>
          <TabsTrigger value="api">API Keys</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Profile Information</CardTitle>
              <CardDescription>Update your personal information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-sm font-medium">First Name</label>
                  <Input defaultValue="John" className="mt-1.5" />
                </div>
                <div>
                  <label className="text-sm font-medium">Last Name</label>
                  <Input defaultValue="Doe" className="mt-1.5" />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">Email</label>
                <Input type="email" defaultValue="john@example.com" className="mt-1.5" />
              </div>
              <div>
                <label className="text-sm font-medium">Username</label>
                <Input defaultValue="johndoe" className="mt-1.5" />
              </div>
              <Button>Save Changes</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Organization</CardTitle>
              <CardDescription>Manage your organization settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Organization Name</label>
                <Input defaultValue="My Studio" className="mt-1.5" />
              </div>
              <div>
                <label className="text-sm font-medium">Role</label>
                <div className="mt-1.5">
                  <Badge>Admin</Badge>
                </div>
              </div>
              <Button>Update Organization</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Change Password</CardTitle>
              <CardDescription>Update your password to keep your account secure</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Current Password</label>
                <Input type="password" className="mt-1.5" />
              </div>
              <div>
                <label className="text-sm font-medium">New Password</label>
                <Input type="password" className="mt-1.5" />
              </div>
              <div>
                <label className="text-sm font-medium">Confirm New Password</label>
                <Input type="password" className="mt-1.5" />
              </div>
              <Button>Update Password</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Two-Factor Authentication</CardTitle>
              <CardDescription>Add an extra layer of security to your account</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-md bg-surface-2">
                    <Smartphone className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Authenticator App</p>
                    <p className="text-xs text-muted-foreground">Use an authenticator app to get codes</p>
                  </div>
                </div>
                <Button variant="outline">Enable</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Email Notifications</CardTitle>
              <CardDescription>Choose what emails you want to receive</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { label: "Render completion", description: "When a render job finishes" },
                { label: "AI generation ready", description: "When AI assets are ready" },
                { label: "Weekly digest", description: "Weekly summary of your activity" },
                { label: "Marketing updates", description: "News about new features" },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{item.label}</p>
                    <p className="text-xs text-muted-foreground">{item.description}</p>
                  </div>
                  <Button variant="outline" size="sm">Enabled</Button>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Appearance Tab */}
        <TabsContent value="appearance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Theme</CardTitle>
              <CardDescription>Customize the look of your dashboard</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="cursor-pointer rounded-md border-2 border-primary bg-slate-900 p-4 text-white">
                  <p className="text-sm font-medium">Dark</p>
                  <p className="text-xs opacity-70">Default</p>
                </div>
                <div className="cursor-pointer rounded-md border border-border bg-white p-4 text-slate-900">
                  <p className="text-sm font-medium">Light</p>
                  <p className="text-xs opacity-70">Coming soon</p>
                </div>
                <div className="cursor-pointer rounded-md border border-border bg-gradient-to-br from-slate-900 to-slate-700 p-4 text-white">
                  <p className="text-sm font-medium">System</p>
                  <p className="text-xs opacity-70">Coming soon</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Keys Tab */}
        <TabsContent value="api" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">API Keys</CardTitle>
              <CardDescription>Manage your API keys for integrations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between rounded-md border border-border p-4">
                <div className="flex items-center gap-3">
                  <Key className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Production Key</p>
                    <p className="text-xs text-muted-foreground font-mono">sk_live_••••••••••••</p>
                  </div>
                </div>
                <Button variant="outline" size="sm">Revoke</Button>
              </div>
              <div className="flex items-center justify-between rounded-md border border-border p-4">
                <div className="flex items-center gap-3">
                  <Key className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Development Key</p>
                    <p className="text-xs text-muted-foreground font-mono">sk_test_••••••••••••</p>
                  </div>
                </div>
                <Button variant="outline" size="sm">Revoke</Button>
              </div>
              <Button variant="outline">
                <Key className="mr-2 h-4 w-4" />
                Generate New Key
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}