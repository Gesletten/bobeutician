"use client"

import React from 'react'
import { IntakeFormData } from '../../lib/models'

type Props = {
    intakeData: IntakeFormData | null
    showProfile: boolean
    setShowProfile: (v: boolean) => void
    reloadIntakeData: () => void
}

export default function InfoPanel({ intakeData, showProfile, setShowProfile, reloadIntakeData }: Props) {
    const prettifyLabel = (s: string | undefined | null) => {
        if (!s) return ''
        return s.replace(/_/g, ' ').replace(/\s+/g, ' ').trim().replace(/(^|\s)\S/g, l => l.toUpperCase())
    }

    return (
        <div className="h-full overflow-y-auto p-4 flex flex-col gap-4">
            {/* Header */}
            <h3 className="font-semibold text-lg text-gray-800 flex items-center gap-2">
                <span>📋</span>
                Your Intake Form Choices
            </h3>

            {/* Info Cards */}
            <div className="flex flex-col gap-3">
                <div className="bg-white rounded-lg p-3 shadow-sm border">
                    <span className="font-medium text-gray-600 block mb-1">Skin Type:</span>
                    <p className={`text-lg font-semibold capitalize ${intakeData?.skin_type ? 'text-blue-600' : 'text-gray-400'}`}>
                        {intakeData?.skin_type ? prettifyLabel(intakeData.skin_type) : 'N/A'}
                    </p>
                    {intakeData?.skin_type && (
                        <span className="text-xs text-gray-500">✅ Completed</span>
                    )}
                </div>

                <div className="bg-white rounded-lg p-3 shadow-sm border">
                    <span className="font-medium text-gray-600 block mb-1">Sensitive Skin:</span>
                    <p className={`text-lg font-semibold capitalize ${intakeData?.sensitive ? 'text-green-600' : 'text-gray-400'}`}>
                        {intakeData?.sensitive === 'yes' ? 'Yes' : intakeData?.sensitive === 'no' ? 'No' : 'N/A'}
                    </p>
                    {intakeData?.sensitive && (
                        <span className="text-xs text-gray-500">✅ Completed</span>
                    )}
                </div>

                <div className="bg-white rounded-lg p-3 shadow-sm border">
                    <span className="font-medium text-gray-600 block mb-1">Main Concerns:</span>
                    <div className="mt-1">
                        {intakeData?.concerns && intakeData.concerns.length > 0 ? (
                            <div className="flex flex-wrap gap-1">
                                {intakeData.concerns.map((concern, index) => (
                                    <span key={index} className="inline-block bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
                                        {prettifyLabel(concern)}
                                    </span>
                                ))}
                                <span className="text-xs text-gray-500 self-center ml-1">✅</span>
                            </div>
                        ) : (
                            <p className="text-lg font-semibold text-gray-400">N/A</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Status and Actions */}
            <div className="flex flex-col gap-2 text-xs">
                <div className="text-gray-600">
                    {intakeData ? (
                        <span className="flex items-center gap-1 flex-wrap">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            <strong>Form completed</strong>
                            {intakeData.completed_at && (
                                <span className="ml-1">on {new Date(intakeData.completed_at).toLocaleDateString()}</span>
                            )}
                            <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Ready for personalized recommendations</span>
                        </span>
                    ) : (
                        <span className="flex items-center gap-1 flex-wrap">
                            <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                            No form data found
                            <span className="ml-2 px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs">Fill intake form for personalized advice</span>
                        </span>
                    )}
                </div>

                <div className="flex flex-wrap items-center gap-2 mt-1">
                    <button onClick={reloadIntakeData} className="text-xs bg-blue-500 text-white px-3 py-1 rounded-full hover:bg-blue-600 transition-colors" title="Refresh intake data">🔄 Refresh</button>
                    <button onClick={() => window.location.href = '/form'} className={`text-xs px-3 py-1 rounded-full transition-colors ${intakeData ? 'bg-purple-600 text-white hover:bg-purple-700' : 'bg-orange-600 text-white hover:bg-orange-700'}`}>{intakeData ? '✏️ Edit Form' : '📝 Fill Form'}</button>
                    {intakeData && (
                        <button onClick={() => setShowProfile(!showProfile)} className="text-xs bg-gray-500 text-white px-3 py-1 rounded-full hover:bg-gray-600 transition-colors">{showProfile ? 'Hide Details' : 'Show Details'}</button>
                    )}
                </div>
            </div>

            {/* Expanded Profile Details */}
            {intakeData && showProfile && (
                <div className="flex flex-col gap-3 mt-2">
                    <div className="bg-white rounded-lg p-3 border">
                        <h4 className="font-medium text-gray-700 mb-2">Complete Profile Summary:</h4>
                        <p className="text-gray-800 text-sm"><strong>Skin:</strong> {prettifyLabel(intakeData.skin_type)} | <strong>Sensitive:</strong> {intakeData.sensitive === 'yes' ? 'Yes' : 'No'}</p>
                        {intakeData.concerns && intakeData.concerns.length > 0 && (
                            <p className="text-gray-800 text-sm mt-1"><strong>Concerns:</strong> {intakeData.concerns.map(c => prettifyLabel(c)).join(', ')}</p>
                        )}
                    </div>

                    <div className="bg-white rounded-lg p-3 border">
                        <h4 className="font-medium text-gray-700 mb-2">AI Consultation Mode:</h4>
                        <p className="text-gray-800 text-sm"><strong>Skincare Mode</strong></p>
                        <p className="text-xs text-gray-600 mt-1">Using your profile for personalized product recommendations with structured format</p>
                    </div>
                </div>
            )}
        </div>
    )
}
