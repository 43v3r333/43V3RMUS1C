"""
Dashboard layout with app structure
*/
import { AppLayout } from "@/components/layout"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <AppLayout>{children}</AppLayout>
}