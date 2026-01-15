import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Simple helper to render intake display text for testing
function IntakeDisplay({ intakeData }: { intakeData: any }) {
    return (
        <div>
            <h2>YOUR INTAKE FORM CHOICES:</h2>
            <div>Skin Type: {intakeData?.skin_type ?? 'N/A'}</div>
            <div>
                Sensitive Skin:{' '}
                {intakeData?.sensitive === 'yes' ? 'Yes' : intakeData?.sensitive === 'no' ? 'No' : 'N/A'}
            </div>
            <div>
                Main Concerns:{' '}
                {intakeData?.concerns && intakeData.concerns.length > 0
                    ? intakeData.concerns.join(', ')
                    : 'N/A'}
            </div>
            <div>
                Status:{' '}
                {intakeData
                    ? `Form completed${intakeData.completed_at ? ` on ${new Date(intakeData.completed_at).toLocaleDateString()}` : ''}`
                    : 'No form data'}
            </div>
        </div>
    );
}

const testScenarios = [
    {
        name: 'Complete Form Data',
        data: {
            skin_type: 'combination',
            sensitive: 'yes',
            concerns: ['acne', 'blackheads', 'enlarged_pores'],
            completed_at: '2025-11-23T10:30:00.000Z'
        }
    },
    {
        name: 'Partial Form Data',
        data: {
            skin_type: 'oily',
            sensitive: 'no',
            concerns: [],
            completed_at: '2025-11-23T09:15:00.000Z'
        }
    },
    {
        name: 'No Form Data',
        data: null
    }
];

describe('IntakeDisplay component', () => {
    testScenarios.forEach((scenario) => {
        test(`renders display correctly for: ${scenario.name}`, () => {
            render(<IntakeDisplay intakeData={scenario.data} />);

            if (scenario.data) {
                const { skin_type, sensitive, concerns, completed_at } = scenario.data;
                expect(screen.getByText(new RegExp(`Skin Type: ${skin_type}`, 'i'))).toBeInTheDocument();
                const sensitiveText = sensitive === 'yes' ? 'Yes' : 'No';
                expect(screen.getByText(new RegExp(`Sensitive Skin: ${sensitiveText}`, 'i'))).toBeInTheDocument();

                if (concerns && concerns.length > 0) {
                    expect(screen.getByText(new RegExp(concerns.join(', '), 'i'))).toBeInTheDocument();
                } else {
                    expect(screen.getByText(/Main Concerns: N\/A/i)).toBeInTheDocument();
                }

                if (completed_at) {
                    const dateStr = new Date(completed_at).toLocaleDateString();
                    expect(screen.getByText(new RegExp(`Form completed on ${dateStr}`))).toBeInTheDocument();
                } else {
                    expect(screen.getByText(/Form completed/i)).toBeInTheDocument();
                }
            } else {
                expect(screen.getByText(new RegExp('Skin Type: N/A', 'i'))).toBeInTheDocument();
                expect(screen.getByText(new RegExp('Sensitive Skin: N/A', 'i'))).toBeInTheDocument();
                expect(screen.getByText(new RegExp('Main Concerns: N/A', 'i'))).toBeInTheDocument();
                expect(screen.getByText(new RegExp('Status: No form data', 'i'))).toBeInTheDocument();
            }
        });
    });
});

// Backend integration tests (mocked fetch)
describe('Backend integration (mocked)', () => {
    const originalFetch = global.fetch;

    beforeAll(() => {

        (global as any).fetch = jest.fn((url: any, _opts?: any) => {
            if (url?.toString().endsWith('/api/chat/intake')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ success: true, id: 'test-intake-id' })
                });
            }

            if (url?.toString().endsWith('/api/qa')) {
                return Promise.resolve({
                    ok: true,
                    json: () =>
                        Promise.resolve({
                            user_profile: { skin_type: 'combination' },
                            recommendation_confidence: 0.92,
                            answer: 'Use a gentle cleanser and niacinamide serum for oily-combination skin.'
                        })
                });
            }

            return Promise.reject(new Error('Unknown endpoint'));
        });
    });

    afterAll(() => {
        global.fetch = originalFetch;
    });

    test('submits intake and receives response', async () => {
        const testData = {
            skin_type: 'combination',
            sensitive: 'yes',
            concerns: ['acne', 'blackheads']
        };

        const intakeResp = await fetch('http://localhost:8000/api/chat/intake', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testData)
        });
        const intakeResult = await intakeResp.json();

        expect(intakeResult).toHaveProperty('success', true);

        const chatResp = await fetch('http://localhost:8000/api/qa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: 'What products should I use?', intake_data: testData })
        });
        const chatResult = await chatResp.json();

        expect(chatResult).toHaveProperty('user_profile');
        expect(chatResult).toHaveProperty('recommendation_confidence');
        expect(chatResult.answer).toMatch(/cleanser|serum|niacinamide/i);
    });
});

export { testScenarios };

