import { z } from 'zod'

export const IntakeSchema = z.object({
  skin: z.string().nonempty(),
  sensitive: z.string().nonempty(),
  concerns: z.array(z.string()).min(1),
})