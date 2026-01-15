// Tests converted from a script to Jest + TypeScript

type IntakeData = {
    skin_type: string;
    sensitive: string;
    concerns?: string[];
    completed_at?: string;
};

describe('BoBeutician intake integration functionality', () => {
    describe('Storage functionality', () => {
        const mockStorage = {
            storage: {} as Record<string, string>,
            getItem(key: string) {
                return this.storage[key] ?? null;
            },
            setItem(key: string, value: string) {
                this.storage[key] = value;
            },
            removeItem(key: string) {
                delete this.storage[key];
            },
            clear() {
                this.storage = {} as Record<string, string>;
            }
        };

        beforeAll(() => {
            (global as any).sessionStorage = mockStorage;
        });

        test('stores and retrieves intake data', () => {
            const testIntakeData: IntakeData = {
                skin_type: 'combination',
                sensitive: 'yes',
                concerns: ['acne', 'blackheads', 'enlarged_pores'],
                completed_at: new Date().toISOString()
            };

            const storageKey = 'bobeutician_intake_form';
            sessionStorage.setItem(storageKey, JSON.stringify(testIntakeData));
            const retrievedRaw = sessionStorage.getItem(storageKey) || 'null';
            const retrievedData = JSON.parse(retrievedRaw) as IntakeData | null;

            expect(retrievedData).not.toBeNull();
            expect(retrievedData).toEqual(testIntakeData);
        });
    });

    describe('Form validation logic', () => {
        function validateForm(formData: Partial<IntakeData>) {
            const errors: string[] = [];
            if (!formData.skin_type) errors.push('Skin type is required');
            if (!formData.sensitive) errors.push('Sensitive skin selection is required');
            return { isValid: errors.length === 0, errors };
        }

        test('valid form passes validation', () => {
            const validForm: Partial<IntakeData> = { skin_type: 'oily', sensitive: 'no', concerns: ['acne'] };
            const result = validateForm(validForm);
            expect(result.isValid).toBe(true);
            expect(result.errors).toHaveLength(0);
        });

        test('invalid form fails validation and returns errors', () => {
            const invalidForm: Partial<IntakeData> = { skin_type: '', sensitive: '', concerns: [] };
            const result = validateForm(invalidForm);
            expect(result.isValid).toBe(false);
            expect(result.errors.length).toBeGreaterThan(0);
            expect(result.errors).toEqual(expect.arrayContaining([
                'Skin type is required',
                'Sensitive skin selection is required'
            ]));
        });
    });

    describe('Data transformation', () => {
        function transformFormData(formData: Partial<IntakeData>) {
            return {
                skin_type: formData.skin_type,
                sensitive: formData.sensitive,
                concerns: formData.concerns ?? [],
                completed_at: new Date().toISOString()
            } as IntakeData;
        }

        test('adds timestamp and preserves fields', () => {
            const raw: Partial<IntakeData> = { skin_type: 'dry', sensitive: 'yes', concerns: ['dryness', 'sensitivity'] };
            const transformed = transformFormData(raw);
            expect(transformed.skin_type).toBe('dry');
            expect(transformed.sensitive).toBe('yes');
            expect(Array.isArray(transformed.concerns)).toBe(true);
            expect(typeof transformed.completed_at).toBe('string');
        });
    });

    describe('N/A display logic', () => {
        function getDisplayValue(value: any, type: 'string' | 'boolean' | 'array' = 'string') {
            if (type === 'array') return value && value.length > 0 ? value.join(', ') : 'N/A';
            if (type === 'boolean') return value === 'yes' ? 'Yes' : value === 'no' ? 'No' : 'N/A';
            return value || 'N/A';
        }

        const cases = [
            { value: 'oily', type: 'string', expected: 'oily' },
            { value: '', type: 'string', expected: 'N/A' },
            { value: null, type: 'string', expected: 'N/A' },
            { value: 'yes', type: 'boolean', expected: 'Yes' },
            { value: 'no', type: 'boolean', expected: 'No' },
            { value: '', type: 'boolean', expected: 'N/A' },
            { value: ['acne', 'dryness'], type: 'array', expected: 'acne, dryness' },
            { value: [], type: 'array', expected: 'N/A' },
            { value: null, type: 'array', expected: 'N/A' }
        ];

        test('returns correct display values for cases', () => {
            for (const c of cases) {
                const out = getDisplayValue(c.value, c.type as any);
                expect(out).toBe(c.expected);
            }
        });
    });

    describe('Chat integration data flow', () => {
        function createChatContext(intakeData: IntakeData | null) {
            if (!intakeData) {
                return {
                    hasProfile: false,
                    welcomeMessage: 'Welcome! Please complete your intake form for personalized advice.',
                    mode: 'general'
                } as const;
            }

            return {
                hasProfile: true,
                welcomeMessage: `Welcome! I can see your profile: ${intakeData.skin_type} skin, ${intakeData.sensitive === 'yes' ? 'sensitive' : 'not sensitive'}${intakeData.concerns && intakeData.concerns.length > 0 ? `, concerns: ${intakeData.concerns.join(', ')}` : ''}.`,
                mode: 'personalized',
                userProfile: {
                    skinType: intakeData.skin_type,
                    sensitive: intakeData.sensitive === 'yes',
                    concerns: intakeData.concerns
                }
            } as const;
        }

        test('complete data produces personalized context', () => {
            const completeData: IntakeData = { skin_type: 'combination', sensitive: 'yes', concerns: ['acne', 'blackheads'] };
            const ctx = createChatContext(completeData);
            expect(ctx.hasProfile).toBe(true);
            expect(ctx.mode).toBe('personalized');
            expect(ctx.welcomeMessage).toMatch(/combination skin/i);
            expect(ctx.userProfile).toEqual(expect.objectContaining({ skinType: 'combination' }));
        });

        test('null data produces general context', () => {
            const ctx = createChatContext(null);
            expect(ctx.hasProfile).toBe(false);
            expect(ctx.mode).toBe('general');
            expect(ctx.welcomeMessage).toMatch(/complete your intake form/i);
        });
    });
});

export { };

