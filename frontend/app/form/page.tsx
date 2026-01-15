import React from 'react'
import IntakeForm from '../../components/form/IntakeForm'
import { colors } from '../../lib/theme'
export default function FormPage() {
  return (
    <section
      className="min-h-screen w-full bg-no-repeat bg-cover bg-center flex items-start justify-center p-6 pt-20 bg-[url('../public/images/form_page_bg.png')]"
      style={{ backgroundColor: colors.background_secondary }}
    >
      <div className="w-full max-w-xl mx-auto">
        <IntakeForm />
      </div>
    </section>
  )
}
