import { useState, useEffect, useRef, type FormEvent } from 'react'
import toast from 'react-hot-toast'
import { useSubmitMemory } from '@/hooks/useSubmitMemory'
import { validateMemoryForm } from '@/lib/validation'
import { getApiErrorMessage } from '@/lib/api'
import { logEvent, TelemetryEvents } from '@/lib/telemetry'
import type { MemoryFormData, MemoryFormErrors } from '@/types/memory'
import type { ApiError } from '@/types/api'

interface MemoryFormProps {
  locationId: number | null
  onBack: () => void
}

const initialFormData: MemoryFormData = {
  businessName: '',
  startYear: '',
  endYear: '',
  note: '',
  proofUrl: '',
}

export function MemoryForm({ locationId, onBack }: MemoryFormProps) {
  const [formData, setFormData] = useState<MemoryFormData>(initialFormData)
  const [errors, setErrors] = useState<MemoryFormErrors>({})
  const [isDirty, setIsDirty] = useState(false)
  const firstErrorRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null)

  const { mutate, isPending, isError, error } = useSubmitMemory()

  useEffect(() => {
    logEvent(TelemetryEvents.MEMORY_FORM_OPENED, {
      location_id: locationId,
    })
  }, [locationId])

  const handleChange = (
    field: keyof MemoryFormData,
    value: string
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    setIsDirty(true)

    setErrors((prev) => {
      const newErrors = { ...prev }
      delete newErrors[field]
      if (newErrors._form) {
        delete newErrors._form
      }
      return newErrors
    })
  }

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()

    if (locationId === null) {
      setErrors({ _form: 'Please select a location on the map first.' })
      return
    }

    logEvent(TelemetryEvents.MEMORY_SUBMIT_STARTED, { location_id: locationId })

    const validationErrors = validateMemoryForm(formData)

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      logEvent(TelemetryEvents.MEMORY_FORM_VALIDATE_FAILED, {
        fields: Object.keys(validationErrors),
      })

      setTimeout(() => {
        const firstErrorField = Object.keys(validationErrors)[0] as keyof MemoryFormData
        const element = document.getElementById(`memory-form-${firstErrorField}`)
        element?.focus()
      }, 0)
      return
    }

    const submissionData = {
      location_id: locationId,
      business_name: formData.businessName.trim(),
      start_year: formData.startYear ? parseInt(formData.startYear, 10) : undefined,
      end_year: formData.endYear ? parseInt(formData.endYear, 10) : undefined,
      note: formData.note.trim() || undefined,
      proof_url: formData.proofUrl.trim() || undefined,
    }

    mutate(submissionData, {
      onSuccess: () => {
        toast.success("Thanks! We'll add that to the history soon.")
        logEvent(TelemetryEvents.MEMORY_SUBMIT_SUCCEEDED, {
          location_id: locationId,
        })

        setFormData(initialFormData)
        setIsDirty(false)
        setErrors({})

        setTimeout(() => onBack(), 1500)
      },
      onError: (error: ApiError) => {
        logEvent(TelemetryEvents.MEMORY_SUBMIT_FAILED, {
          location_id: locationId,
          code: error.code,
        })

        if (error.code === 'rate_limited') {
          const retrySeconds = error.retryAfterMs
            ? Math.ceil(error.retryAfterMs / 1000)
            : 'a few'
          setErrors({
            _form: `We're getting a lot of requests—try again in ${retrySeconds} seconds`,
          })
        } else {
          setErrors({
            _form: getApiErrorMessage(error),
          })
        }
      },
    })
  }

  const handleBack = () => {
    if (isDirty) {
      const confirmed = window.confirm(
        'You have unsaved changes. Are you sure you want to go back?'
      )
      if (!confirmed) return
    }
    onBack()
  }

  const noteLength = formData.note.length
  const isNoteOverLimit = noteLength > 240

  const hasErrors = Object.keys(errors).length > 0

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6"
      aria-label="Memory submission form"
      noValidate
    >
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={handleBack}
          className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 flex items-center gap-1 text-sm font-medium"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to history
        </button>
      </div>

      {errors._form && (
        <div
          className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
          role="alert"
        >
          <p className="text-sm text-red-800 dark:text-red-200">
            {errors._form}
          </p>
        </div>
      )}

      {locationId === null && (
        <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            Tap a pin on the map to attach your memory to a spot.
          </p>
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label
            htmlFor="memory-form-businessName"
            className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-1"
          >
            Business Name <span className="text-red-600">*</span>
          </label>
          <input
            id="memory-form-businessName"
            type="text"
            value={formData.businessName}
            onChange={(e) => handleChange('businessName', e.target.value)}
            placeholder="e.g., Mario's Pizza"
            maxLength={255}
            autoComplete="off"
            autoFocus
            disabled={isPending}
            aria-required="true"
            aria-invalid={!!errors.businessName}
            aria-describedby={
              errors.businessName ? 'error-businessName' : undefined
            }
            className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.businessName
                ? 'border-red-500 dark:border-red-400'
                : 'border-gray-300 dark:border-gray-600'
            }`}
          />
          {errors.businessName && (
            <p
              id="error-businessName"
              className="mt-1 text-sm text-red-600 dark:text-red-400"
              role="alert"
            >
              {errors.businessName}
            </p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="memory-form-startYear"
              className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-1"
            >
              Start Year
            </label>
            <input
              id="memory-form-startYear"
              type="text"
              inputMode="numeric"
              pattern="\d{4}"
              value={formData.startYear}
              onChange={(e) => handleChange('startYear', e.target.value)}
              placeholder="YYYY"
              maxLength={4}
              autoComplete="off"
              disabled={isPending}
              aria-invalid={!!errors.startYear}
              aria-describedby={
                errors.startYear ? 'error-startYear' : undefined
              }
              className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.startYear
                  ? 'border-red-500 dark:border-red-400'
                  : 'border-gray-300 dark:border-gray-600'
              }`}
            />
            {errors.startYear && (
              <p
                id="error-startYear"
                className="mt-1 text-sm text-red-600 dark:text-red-400"
                role="alert"
              >
                {errors.startYear}
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="memory-form-endYear"
              className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-1"
            >
              End Year
            </label>
            <input
              id="memory-form-endYear"
              type="text"
              inputMode="numeric"
              pattern="\d{4}"
              value={formData.endYear}
              onChange={(e) => handleChange('endYear', e.target.value)}
              placeholder="YYYY"
              maxLength={4}
              autoComplete="off"
              disabled={isPending}
              aria-invalid={!!errors.endYear}
              aria-describedby={errors.endYear ? 'error-endYear' : undefined}
              className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.endYear
                  ? 'border-red-500 dark:border-red-400'
                  : 'border-gray-300 dark:border-gray-600'
              }`}
            />
            {errors.endYear && (
              <p
                id="error-endYear"
                className="mt-1 text-sm text-red-600 dark:text-red-400"
                role="alert"
              >
                {errors.endYear}
              </p>
            )}
          </div>
        </div>

        <div>
          <label
            htmlFor="memory-form-note"
            className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-1"
          >
            Your Story <span className="text-red-600">*</span>
          </label>
          <textarea
            id="memory-form-note"
            value={formData.note}
            onChange={(e) => handleChange('note', e.target.value)}
            placeholder="What do you remember about this place?"
            rows={4}
            maxLength={240}
            disabled={isPending}
            aria-required="true"
            aria-invalid={!!errors.note}
            aria-describedby={errors.note ? 'error-note' : 'note-counter'}
            className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
              errors.note
                ? 'border-red-500 dark:border-red-400'
                : 'border-gray-300 dark:border-gray-600'
            }`}
          />
          <div className="mt-1 flex items-center justify-between">
            <div className="flex-1">
              {errors.note && (
                <p
                  id="error-note"
                  className="text-sm text-red-600 dark:text-red-400"
                  role="alert"
                >
                  {errors.note}
                </p>
              )}
            </div>
            <p
              id="note-counter"
              className={`text-xs ${
                isNoteOverLimit
                  ? 'text-red-600 dark:text-red-400 font-medium'
                  : 'text-gray-500 dark:text-gray-400'
              }`}
              aria-live="polite"
            >
              {noteLength}/240
            </p>
          </div>
        </div>

        <div>
          <label
            htmlFor="memory-form-proofUrl"
            className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-1"
          >
            Proof Link (optional)
          </label>
          <input
            id="memory-form-proofUrl"
            type="url"
            value={formData.proofUrl}
            onChange={(e) => handleChange('proofUrl', e.target.value)}
            placeholder="https://example.com/article"
            autoComplete="off"
            disabled={isPending}
            aria-invalid={!!errors.proofUrl}
            aria-describedby={
              errors.proofUrl ? 'error-proofUrl' : 'helper-proofUrl'
            }
            className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.proofUrl
                ? 'border-red-500 dark:border-red-400'
                : 'border-gray-300 dark:border-gray-600'
            }`}
          />
          {!errors.proofUrl && (
            <p
              id="helper-proofUrl"
              className="mt-1 text-xs text-gray-500 dark:text-gray-400"
            >
              Link to an article, review, or post
            </p>
          )}
          {errors.proofUrl && (
            <p
              id="error-proofUrl"
              className="mt-1 text-sm text-red-600 dark:text-red-400"
              role="alert"
            >
              {errors.proofUrl}
            </p>
          )}
        </div>
      </div>

      <div className="sticky bottom-0 -mx-4 -mb-4 p-4 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
        <button
          type="submit"
          disabled={!locationId || isPending || hasErrors}
          className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {isPending && (
            <svg
              className="animate-spin h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          )}
          {isPending ? 'Submitting...' : 'Submit'}
        </button>
      </div>
    </form>
  )
}
