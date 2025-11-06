import { useState, useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useNavigate } from 'react-router-dom'
import { familiesApi, childrenApi, recommendationsApi } from '@/lib/api'
import type { Family } from '@/types/family'
import type { ChildProfile } from '@/types/child'
import type { Recommendation } from '@/types/recommendation'

export function DashboardPage() {
  const { user, clearAuth } = useAuthStore()
  const navigate = useNavigate()

  const [family, setFamily] = useState<Family | null>(null)
  const [children, setChildren] = useState<ChildProfile[]>([])
  const [recommendations, setRecommendations] = useState<Record<number, Recommendation[]>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Form states
  const [showFamilyForm, setShowFamilyForm] = useState(false)
  const [showChildForm, setShowChildForm] = useState(false)
  const [generatingForChild, setGeneratingForChild] = useState<number | null>(null)

  // Family form fields
  const [familyForm, setFamilyForm] = useState({
    city: '',
    state: '',
    zip_code: '',
    timezone: 'America/Los_Angeles',
    budget_monthly: '',
  })

  // Child form fields
  const [childForm, setChildForm] = useState({
    name: '',
    birth_date: '',
    primary_goal: '',
    notes: '',
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError('')

      // Try to get family profile
      try {
        const familyData = await familiesApi.getMyFamily()
        setFamily(familyData)

        // If family exists, load children
        const childrenData = await childrenApi.list()
        setChildren(childrenData)

        // Load existing recommendations for each child
        const recsPromises = childrenData.map(async (child) => {
          try {
            const recs = await recommendationsApi.get(child.id)
            return { childId: child.id, recs }
          } catch {
            return { childId: child.id, recs: [] }
          }
        })
        const recsResults = await Promise.all(recsPromises)
        const recsMap: Record<number, Recommendation[]> = {}
        recsResults.forEach(({ childId, recs }) => {
          if (recs.length > 0) {
            recsMap[childId] = recs
          }
        })
        setRecommendations(recsMap)
      } catch (err: any) {
        // Family not found is OK - user needs to create one
        if (err.response?.status !== 404) {
          throw err
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateFamily = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setError('')
      const familyData = await familiesApi.create({
        city: familyForm.city || undefined,
        state: familyForm.state || undefined,
        zip_code: familyForm.zip_code || undefined,
        timezone: familyForm.timezone,
        budget_monthly: familyForm.budget_monthly ? parseInt(familyForm.budget_monthly) * 100 : undefined, // Convert dollars to cents
      })
      setFamily(familyData)
      setShowFamilyForm(false)
      setFamilyForm({ city: '', state: '', zip_code: '', timezone: 'America/Los_Angeles', budget_monthly: '' })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create family profile')
    }
  }

  const handleCreateChild = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!family) {
      setError('Please create a family profile first')
      return
    }

    try {
      setError('')
      const childData = await childrenApi.create({
        name: childForm.name,
        birth_date: childForm.birth_date,
        primary_goal: childForm.primary_goal || undefined,
        notes: childForm.notes || undefined,
      })
      setChildren([...children, childData])
      setShowChildForm(false)
      setChildForm({ name: '', birth_date: '', primary_goal: '', notes: '' })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create child profile')
    }
  }

  const handleGenerateRecommendations = async (childId: number) => {
    try {
      setError('')
      setGeneratingForChild(childId)
      const recs = await recommendationsApi.generate({
        child_profile_id: childId,
        max_activities: 5,
      })
      setRecommendations({ ...recommendations, [childId]: recs })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate recommendations')
    } finally {
      setGeneratingForChild(null)
    }
  }

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Compass</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">{user?.email}</span>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {error && (
            <div className="mb-4 rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Welcome to Compass!
            </h2>
            <p className="text-gray-600 mb-4">
              Your personalized activity advisor for finding the best enrichment activities for your child.
            </p>
          </div>

          {/* Family Profile Section */}
          {!family ? (
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Create Your Family Profile
              </h3>
              {!showFamilyForm ? (
                <div>
                  <p className="text-gray-600 mb-4">
                    Get started by creating your family profile. This helps us provide better recommendations.
                  </p>
                  <button
                    onClick={() => setShowFamilyForm(true)}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                  >
                    Create Family Profile
                  </button>
                </div>
              ) : (
                <form onSubmit={handleCreateFamily} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        City
                      </label>
                      <input
                        type="text"
                        value={familyForm.city}
                        onChange={(e) => setFamilyForm({ ...familyForm, city: e.target.value })}
                        className="w-full rounded-md border border-gray-300 px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        State
                      </label>
                      <input
                        type="text"
                        value={familyForm.state}
                        onChange={(e) => setFamilyForm({ ...familyForm, state: e.target.value })}
                        className="w-full rounded-md border border-gray-300 px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        ZIP Code
                      </label>
                      <input
                        type="text"
                        value={familyForm.zip_code}
                        onChange={(e) => setFamilyForm({ ...familyForm, zip_code: e.target.value })}
                        className="w-full rounded-md border border-gray-300 px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Monthly Budget ($)
                      </label>
                      <input
                        type="number"
                        value={familyForm.budget_monthly}
                        onChange={(e) => setFamilyForm({ ...familyForm, budget_monthly: e.target.value })}
                        className="w-full rounded-md border border-gray-300 px-3 py-2"
                        placeholder="e.g., 500"
                      />
                    </div>
                  </div>
                  <div className="flex space-x-3">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                    >
                      Create Profile
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowFamilyForm(false)}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>
          ) : (
            <>
              {/* Family Info */}
              <div className="bg-white shadow rounded-lg p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Family Profile
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {family.city && (
                    <div>
                      <span className="text-sm text-gray-500">City:</span>
                      <span className="ml-2 text-gray-900">{family.city}</span>
                    </div>
                  )}
                  {family.state && (
                    <div>
                      <span className="text-sm text-gray-500">State:</span>
                      <span className="ml-2 text-gray-900">{family.state}</span>
                    </div>
                  )}
                  {family.zip_code && (
                    <div>
                      <span className="text-sm text-gray-500">ZIP Code:</span>
                      <span className="ml-2 text-gray-900">{family.zip_code}</span>
                    </div>
                  )}
                  {family.budget_monthly && (
                    <div>
                      <span className="text-sm text-gray-500">Monthly Budget:</span>
                      <span className="ml-2 text-gray-900">
                        ${(family.budget_monthly / 100).toFixed(2)}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Children Section */}
              <div className="bg-white shadow rounded-lg p-6 mb-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Children ({children.length})
                  </h3>
                  {!showChildForm && (
                    <button
                      onClick={() => setShowChildForm(true)}
                      className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 text-sm"
                    >
                      Add Child
                    </button>
                  )}
                </div>

                {showChildForm && (
                  <form onSubmit={handleCreateChild} className="mb-6 p-4 bg-gray-50 rounded-lg space-y-4">
                    <h4 className="font-medium text-gray-900">Add New Child</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Name *
                        </label>
                        <input
                          type="text"
                          required
                          value={childForm.name}
                          onChange={(e) => setChildForm({ ...childForm, name: e.target.value })}
                          className="w-full rounded-md border border-gray-300 px-3 py-2"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Birth Date *
                        </label>
                        <input
                          type="date"
                          required
                          value={childForm.birth_date}
                          onChange={(e) => setChildForm({ ...childForm, birth_date: e.target.value })}
                          className="w-full rounded-md border border-gray-300 px-3 py-2"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Primary Goal
                        </label>
                        <input
                          type="text"
                          value={childForm.primary_goal}
                          onChange={(e) => setChildForm({ ...childForm, primary_goal: e.target.value })}
                          className="w-full rounded-md border border-gray-300 px-3 py-2"
                          placeholder="e.g., Build confidence, Make friends"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Notes
                        </label>
                        <textarea
                          value={childForm.notes}
                          onChange={(e) => setChildForm({ ...childForm, notes: e.target.value })}
                          className="w-full rounded-md border border-gray-300 px-3 py-2"
                          rows={2}
                        />
                      </div>
                    </div>
                    <div className="flex space-x-3">
                      <button
                        type="submit"
                        className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                      >
                        Add Child
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowChildForm(false)}
                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                )}

                {children.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    No children added yet. Click "Add Child" to get started.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {children.map((child) => (
                      <div key={child.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-semibold text-gray-900">{child.name}</h4>
                            <p className="text-sm text-gray-500">
                              Age {child.age} • {child.primary_goal || 'No goal set'}
                            </p>
                          </div>
                          <button
                            onClick={() => handleGenerateRecommendations(child.id)}
                            disabled={generatingForChild === child.id}
                            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                          >
                            {generatingForChild === child.id ? 'Generating...' : 'Get Recommendations'}
                          </button>
                        </div>

                        {/* Recommendations for this child */}
                        {recommendations[child.id] && recommendations[child.id].length > 0 && (
                          <div className="mt-4 pt-4 border-t border-gray-200">
                            <h5 className="font-medium text-gray-900 mb-3">Recommendations</h5>
                            <div className="space-y-3">
                              {recommendations[child.id].map((rec) => (
                                <div key={rec.id} className="bg-gray-50 rounded-lg p-4">
                                  <div className="flex justify-between items-start mb-2">
                                    <div>
                                      <h6 className="font-semibold text-gray-900">{rec.activity_name}</h6>
                                      <p className="text-sm text-gray-600">{rec.provider_name}</p>
                                    </div>
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                                      rec.tier === 'primary' ? 'bg-green-100 text-green-800' :
                                      rec.tier === 'budget_saver' ? 'bg-blue-100 text-blue-800' :
                                      'bg-purple-100 text-purple-800'
                                    }`}>
                                      {rec.tier}
                                    </span>
                                  </div>
                                  <div className="text-sm text-gray-600 mb-2">
                                    <span className="font-medium">Score: {rec.total_score.toFixed(1)}</span>
                                    <span className="ml-4 text-gray-500">
                                      Fit: {rec.fit_score.toFixed(1)} • Practical: {rec.practical_score.toFixed(1)} • Goals: {rec.goals_score.toFixed(1)}
                                    </span>
                                  </div>
                                  {rec.explanation && (
                                    <p className="text-sm text-gray-700 mt-2">{rec.explanation}</p>
                                  )}
                                  {rec.why_good_fit && rec.why_good_fit.length > 0 && (
                                    <div className="mt-2">
                                      <p className="text-xs font-medium text-gray-700 mb-1">Why it's a good fit:</p>
                                      <ul className="text-xs text-gray-600 list-disc list-inside">
                                        {rec.why_good_fit.map((reason, idx) => (
                                          <li key={idx}>{reason}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}
