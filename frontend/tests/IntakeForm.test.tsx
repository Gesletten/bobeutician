/// <reference types="jest" />

import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import IntakeForm from '../components/form/IntakeForm'
import useIntake from '../hooks/useIntake'

jest.mock('../hooks/useIntake')

describe('IntakeForm', () => {
    const mockSave = jest.fn()

    beforeEach(() => {
        jest.clearAllMocks()

            ; (useIntake as jest.Mock).mockReturnValue({
                data: {},
                save: mockSave,
            })
    })

    test('renders the intakeForm correctly', () => {
        render(<IntakeForm />)
        expect(screen.getByText(/What is your skin type/i)).toBeInTheDocument()
        expect(screen.getByText(/Do you have sensitive skin/i)).toBeInTheDocument()
        expect(screen.getByText(/What are your main skin concerns/i)).toBeInTheDocument()
    })

    test('updates radio inputs (skin type)', () => {
        render(<IntakeForm />)

        const oilyRadio = screen.getByLabelText(/oily/i)
        fireEvent.click(oilyRadio)

        expect(oilyRadio).toBeChecked()
    })

    test('updates radio inputs (concerns)', () => {
        render(<IntakeForm />)

        const acneCheck = screen.getByLabelText(/acne/i)
        fireEvent.click(acneCheck)

        expect(acneCheck).toBeChecked()
    })

    test('shows error correctly when blank form is submitted', () => {
        const { container } = render(<IntakeForm />)

        // The submit button is disabled when required fields are missing.
        // Submit the form directly to trigger validation and error handling.
        const form = container.querySelector('form') as HTMLFormElement
        fireEvent.submit(form)

        expect(screen.getByText(/Please fill out all required fields\./i)).toBeInTheDocument()
    })

    /*test('renders link to chat page', () => {
        render(<IntakeForm />)
        const chat = screen.getByText(/proceed with chat/i)
        expect(chat).toHaveAttribute('href', '/chat')
    })*/
})

