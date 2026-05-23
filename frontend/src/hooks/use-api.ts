"""
React Query hooks for API interactions
*/
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuthStore } from "@/stores"

// Auth hooks
export function useLogin() {
  const { setAuth } = useAuthStore()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: { username: string; password: string }) => api.auth.login(data),
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token)
      queryClient.invalidateQueries({ queryKey: ["user"] })
    },
  })
}

export function useLogout() {
  const { logout } = useAuthStore()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => api.auth.logout(),
    onSuccess: () => {
      logout()
      queryClient.clear()
    },
  })
}

export function useCurrentUser() {
  return useQuery({
    queryKey: ["user"],
    queryFn: api.users.me,
    enabled: useAuthStore.getState().isAuthenticated,
  })
}

// Media hooks
export function useArtists(params?: { skip?: number; limit?: number; genre?: string }) {
  return useQuery({
    queryKey: ["artists", params],
    queryFn: () => api.media.artists.list(params),
  })
}

export function useProjects(params?: { skip?: number; limit?: number; status?: string }) {
  return useQuery({
    queryKey: ["projects", params],
    queryFn: () => api.media.projects.list(params),
  })
}

export function useProject(id: string) {
  return useQuery({
    queryKey: ["project", id],
    queryFn: () => api.media.projects.get(id),
    enabled: !!id,
  })
}

// Asset hooks
export function useMediaAssets(params?: { skip?: number; limit?: number; asset_type?: string }) {
  return useQuery({
    queryKey: ["media-assets", params],
    queryFn: () => api.assets.media.list(params),
  })
}

export function useGeneratedAssets(params?: { skip?: number; limit?: number; asset_type?: string }) {
  return useQuery({
    queryKey: ["generated-assets", params],
    queryFn: () => api.assets.generated.list(params),
  })
}

export function useRecentAssets(limit?: number) {
  return useQuery({
    queryKey: ["recent-assets", limit],
    queryFn: () => api.assets.generated.recent(limit),
  })
}

// Workflow hooks
export function useRenderJobs(params?: { skip?: number; limit?: number; status?: string }) {
  return useQuery({
    queryKey: ["render-jobs", params],
    queryFn: () => api.workflows.jobs.list(params),
  })
}

export function usePrompts(params?: { skip?: number; limit?: number; prompt_type?: string }) {
  return useQuery({
    queryKey: ["prompts", params],
    queryFn: () => api.workflows.prompts.list(params),
  })
}

// Health hook
export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: api.health.check,
    refetchInterval: 30000, // Refetch every 30 seconds
  })
}