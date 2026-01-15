"use client";

import React, { useState, useEffect } from 'react'
// Removed unused imports: `z`, `IntakeSchema`, and `Button`
import Input from '../../ui/Input'
import RadioGroup from '../../ui/RadioGroup'
import { colors } from '../../lib/theme'
import { skincareStorage } from '../../lib/storage'
import { IntakeFormData } from '../../lib/models'
import { submitIntakeForm } from '../../lib/api'

export default function IntakeForm() {
  const [form, setForm] = useState<{
    skin_type: string
    sensitive: string
    concerns: string[]
  }>({
    skin_type: '',
    sensitive: '',
    concerns: [],
  })

  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Load existing data on mount and persist across navigation
  useEffect(() => {
    console.log('IntakeForm mounted - checking for existing data')

    const existingData = skincareStorage.getIntakeForm()
    if (existingData) {
      console.log('Loading existing intake data:', existingData)
      setForm({
        skin_type: existingData.skin_type || '',
        sensitive: existingData.sensitive || '',
        concerns: existingData.concerns || []
      })
    } else {
      console.log('No existing data found - starting fresh')
    }

    // No cleanup on unmount - data should persist when navigating to chat
  }, [])

  function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
    const { name, value, checked, type } = event.target
    if (type === "checkbox" && name === "concerns") {
      setForm((prev) => {
        const newConcerns = checked
          ? [...prev.concerns, value]
          : prev.concerns.filter(item => item !== value);

        return { ...prev, concerns: newConcerns };
      })
    } else {
      setForm(prev => ({ ...prev, [name]: value }))
    }
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      console.log('Submitting form with data:', form)

      // Validate form data
      if (!form.skin_type || !form.sensitive) {
        setError('Please fill out all required fields.')
        setIsLoading(false)
        return
      }

      // Create intake data object
      const intakeData: IntakeFormData = {
        skin_type: form.skin_type as 'oily' | 'dry' | 'normal' | 'combination' | 'sensitive',
        sensitive: form.sensitive as 'yes' | 'no',
        concerns: form.concerns,
        completed_at: new Date().toISOString()
      }

      console.log('Saving intake data:', intakeData)

      // Save directly to sessionStorage first
      try {
        const serializedData = JSON.stringify(intakeData)
        sessionStorage.setItem('bobeutician_intake_form', serializedData)

        // Verify save
        const verification = sessionStorage.getItem('bobeutician_intake_form')
        if (!verification) {
          throw new Error('Session storage save failed')
        }

        console.log('Data saved to session storage successfully')

        // Also save using our storage system
        const saveResult = skincareStorage.saveIntakeForm(intakeData)
        console.log('Storage system save result:', saveResult)

      } catch (storageError) {
        console.error('Storage failed:', storageError)
        setError('Failed to save form data. Please try again.')
        setIsLoading(false)
        return
      }

      // Submit to backend (optional) using shared API helper
      try {
        await submitIntakeForm(intakeData)
        console.log('Backend submission successful')
      } catch (backendError) {
        console.warn('Backend submission failed (continuing anyway):', backendError)
      }

      // Redirect to chat
      console.log('Redirecting to chat...')
      window.location.href = "/chat"

    } catch (error: any) {
      console.error('Failed to save intake form:', error)
      setError(`Failed to save your information: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-xl mx-auto bg-white p-4 md:p-6 rounded-lg shadow accent-[#260000] text-base"
      style={{ backgroundColor: colors.background_secondary }}
    >
      {/* Intake Form Notice */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-3">
          <span className="text-blue-600 text-lg">📋</span>
          <div>
            <p className="text-blue-800 font-medium text-sm">Fill Out Your Skin Profile</p>
            <p className="text-blue-700 text-xs mt-1">
              Your form data will be saved and available in the chat. Data clears only when you close the chat interface.
            </p>
          </div>
        </div>
      </div>
      <fieldset>
        <legend className="font-medium text-[#260000] mb-2">
          What is your skin type?
        </legend>
        <RadioGroup>
          <label className="flex items-center gap-2">
            <Input
              type="radio"
              name="skin_type"
              value="dry"
              checked={form.skin_type === 'dry'}
              onChange={handleChange}
              required
            />
            dry
          </label>
          <label className="flex items-center gap-2">
            <Input
              type="radio"
              name="skin_type"
              value="oily"
              checked={form.skin_type === 'oily'}
              onChange={handleChange}
              required
            />
            oily
          </label>
          <label className="flex items-center gap-2">
            <Input
              type="radio"
              name="skin_type"
              value="combination"
              checked={form.skin_type === 'combination'}
              onChange={handleChange}
              required
            />
            combination
          </label>
          <label className="flex items-center gap-2">
            <Input
              type="radio"
              name="skin_type"
              value="normal"
              checked={form.skin_type === 'normal'}
              onChange={handleChange}
              required
            />
            normal
          </label>
        </RadioGroup>

      </fieldset>
      <fieldset>

        <legend className="font-medium text-[#260000] mb-2">
          Do you have sensitive skin?
        </legend>
        <RadioGroup>
          <label className="flex items-center gap-2">
            <Input
              type="radio"
              name="sensitive"
              value="yes"
              checked={form.sensitive === 'yes'}
              onChange={handleChange}
              required
            />
            yes
          </label>
          <label className="flex items-center gap-2">
            <Input
              type="radio"
              name="sensitive"
              value="no"
              checked={form.sensitive === 'no'}
              onChange={handleChange}
              required
            />
            no
          </label>
        </RadioGroup>
      </fieldset>
      <fieldset>
        <legend className="font-medium text-[#260000] mb-2">
          What are your main skin concerns? (Optional)
        </legend>
        <label className="flex items-center gap-2">
          <Input
            type="checkbox"
            name="concerns"
            value="acne"
            checked={form.concerns.includes('acne')}
            onChange={handleChange}
          />
          acne
        </label>
        <label className="flex items-center gap-2">
          <Input
            type="checkbox"
            name="concerns"
            value="aging"
            checked={form.concerns.includes('aging')}
            onChange={handleChange}
          />
          aging
        </label>
        <label className="flex items-center gap-2">
          <Input
            type="checkbox"
            name="concerns"
            value="pigmentation"
            checked={form.concerns.includes('pigmentation')}
            onChange={handleChange}
          />
          pigmentation
        </label>
        <label className="flex items-center gap-2">
          <Input
            type="checkbox"
            name="concerns"
            value="dryness"
            checked={form.concerns.includes('dryness')}
            onChange={handleChange}
          />
          dryness
        </label>
        <label className="flex items-center gap-2">
          <Input
            type="checkbox"
            name="concerns"
            value="blackheads"
            checked={form.concerns.includes('blackheads')}
            onChange={handleChange}
          />
          blackheads
        </label>
        <label className="flex items-center gap-2">
          <Input
            type="checkbox"
            name="concerns"
            value="sun_damage"
            checked={form.concerns.includes('sun_damage')}
            onChange={handleChange}
          />
          sun damage
        </label>
      </fieldset>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      <div className="flex justify-center items-center">

        <button
          type="submit"
          disabled={isLoading || !form.skin_type || !form.sensitive}
          className="mt-6 px-5 py-2 bg-[#DEA193] text-white text-xl font-semibold rounded-full shadow-md hover:bg-[#c78f80] disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200"
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              Saving...
            </div>
          ) : (
            'Proceed with chat'
          )}
        </button>
      </div>

      {/* Debug info in development */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-4 p-2 bg-gray-100 rounded text-xs">
          <strong>Debug:</strong> {JSON.stringify(form)}
        </div>
      )}
    </form>
  )
}