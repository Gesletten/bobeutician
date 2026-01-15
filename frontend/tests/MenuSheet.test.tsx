/// <reference types="jest" />
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import MenuSheet from "../components/common/MenuSheet"
import { describe, expect, test } from '@jest/globals'

describe('MenuSheet', () => {
    test('renders three menu links with correct hrefs and labels', () => {
        // Render the component
        render(<MenuSheet />)

        // There should be three links
        const links = screen.getAllByRole('link')
        expect(links).toHaveLength(3)

        // Check each link by accessible name and href
        const about = screen.getByRole('link', { name: /about/i })
        const form = screen.getByRole('link', { name: /form/i })
        const chat = screen.getByRole('link', { name: /chat/i })
        
        expect(about).not.toBeNull()
        expect(about.getAttribute('href')).toBe('/')

        expect(form).not.toBeNull()
        expect(form.getAttribute('href')).toBe('/form')

        expect(chat).not.toBeNull()
        expect(chat.getAttribute('href')).toBe('/chat')
    })
})
