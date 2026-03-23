import { useEffect, useState } from 'react'
import Sidebar from '../components/Sidebar'
import { authAPI, authHelpers } from '../services/api'

const formatJoinedDate = (value) => {
  if (!value) {
    return 'Not available'
  }

  try {
    return new Intl.DateTimeFormat('en-IN', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(value))
  } catch {
    return value
  }
}

const Profile = () => {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await authAPI.getProfile()
        setProfile(data)
        authHelpers.setAuthData(
          authHelpers.getToken(),
          data.role || authHelpers.getUserRole(),
          data.username || authHelpers.getUsername()
        )
        setError('')
      } catch (err) {
        console.error(err)
        setError('Profile load nahi ho payi. Thoda refresh karke try karo.')
      } finally {
        setLoading(false)
      }
    }

    loadProfile()
  }, [])

  const displayName =
    profile?.first_name || profile?.last_name
      ? `${profile.first_name || ''} ${profile.last_name || ''}`.trim()
      : profile?.username || authHelpers.getUsername() || 'User'

  const initial = displayName.charAt(0).toUpperCase()

  return (
    <div className="flex">
      <Sidebar />
      <div className="min-h-[calc(100vh-64px)] flex-1 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 px-4 py-12">
        <div className="absolute top-0 left-0 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-500/10 blur-3xl opacity-20"></div>
        <div className="absolute bottom-0 right-0 h-96 w-96 translate-x-1/2 translate-y-1/2 rounded-full bg-purple-500/10 blur-3xl opacity-20"></div>

        <div className="relative z-10 mx-auto max-w-5xl">
          <div className="mb-10 text-center">
            <h1 className="mb-4 text-5xl font-bold text-white">
              Your <span className="gradient-text">Profile</span>
            </h1>
            <p className="mx-auto max-w-2xl text-lg text-gray-400">
              Yahan par login user ki basic details dikhengi.
            </p>
          </div>

          {loading && (
            <div className="card text-center py-16">
              <div className="inline-block">
                <div className="loading-spinner mb-4"></div>
                <p className="text-gray-400">Profile load ho rahi hai...</p>
              </div>
            </div>
          )}

          {error && !loading && (
            <div className="card mb-8 border border-red-500/30 bg-red-500/10 text-center py-8">
              <p className="font-medium text-red-300">{error}</p>
            </div>
          )}

          {profile && !loading && (
            <>
              <div className="card mb-8 border border-blue-500/20 bg-slate-900/50">
                <div className="flex flex-col items-center gap-6 md:flex-row md:items-center md:justify-between">
                  <div className="flex items-center gap-5">
                    <div className="flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-3xl font-bold text-white shadow-lg shadow-blue-500/30">
                      {initial}
                    </div>
                    <div>
                      <p className="text-sm uppercase tracking-[0.25em] text-blue-300/80">
                        Logged In User
                      </p>
                      <h2 className="mt-2 text-3xl font-bold text-white">{displayName}</h2>
                      <p className="mt-2 text-gray-400">@{profile.username}</p>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-blue-500/20 bg-blue-500/10 px-5 py-4 text-center">
                    <p className="text-xs uppercase tracking-[0.2em] text-blue-200/80">Role</p>
                    <p className="mt-2 text-xl font-semibold capitalize text-white">
                      {profile.role || 'investor'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid gap-6 md:grid-cols-2">
                <div className="card card-hover">
                  <p className="mb-2 text-sm font-medium text-gray-400">Username</p>
                  <p className="text-2xl font-bold text-white">{profile.username}</p>
                  <p className="mt-3 text-sm text-gray-500">
                    Yeh unique handle hai jo account me use hota hai.
                  </p>
                </div>

                <div className="card card-hover">
                  <p className="mb-2 text-sm font-medium text-gray-400">Email</p>
                  <p className="break-all text-2xl font-bold text-white">
                    {profile.email || 'Not added'}
                  </p>
                  <p className="mt-3 text-sm text-gray-500">
                    Account communication ke liye linked email.
                  </p>
                </div>

                <div className="card card-hover">
                  <p className="mb-2 text-sm font-medium text-gray-400">Full Name</p>
                  <p className="text-2xl font-bold text-white">{displayName}</p>
                  <p className="mt-3 text-sm text-gray-500">
                    First name aur last name backend profile se aa rahe hain.
                  </p>
                </div>

                <div className="card card-hover">
                  <p className="mb-2 text-sm font-medium text-gray-400">Joined On</p>
                  <p className="text-2xl font-bold text-white">
                    {formatJoinedDate(profile.date_joined)}
                  </p>
                  <p className="mt-3 text-sm text-gray-500">
                    Account create hone ka time yahan dikh raha hai.
                  </p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Profile
