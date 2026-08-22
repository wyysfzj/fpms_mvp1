/// <reference types="vite/client" />

import { recordFeeObligationInstruction } from '../fees'
import type {
    FeeObligationInstructionPayload,
    FeeObligationInstructionResult,
} from '../fees.types'

type Exact<Actual, Expected> = [Actual] extends [Expected]
    ? [Expected] extends [Actual]
        ? true
        : false
    : false

const payload: FeeObligationInstructionPayload = {
    instruction: 'PAY',
    idempotency_key: 'instruction-key-1',
}

const resultPromise: Promise<FeeObligationInstructionResult> =
    recordFeeObligationInstruction('obligation-1', payload)

declare const result: FeeObligationInstructionResult

const payloadInstruction: Exact<
    FeeObligationInstructionPayload['instruction'],
    'PAY' | 'HOLD' | 'ABANDON'
> = true
const obligationId: string = result.obligation_id
const activityId: string = result.activity_id
const serverStatus: Exact<
    FeeObligationInstructionResult['client_instruction_status'],
    'PENDING' | 'PAY' | 'HOLD' | 'ABANDON'
> = true
const idempotencyKey: string = result.idempotency_key
const reused: boolean = result.reused

recordFeeObligationInstruction('obligation-1', {
    instruction: 'HOLD',
    idempotency_key: 'instruction-key-2',
})

recordFeeObligationInstruction('obligation-1', {
    instruction: 'ABANDON',
    idempotency_key: 'instruction-key-3',
})

recordFeeObligationInstruction('obligation-1', {
    // @ts-expect-error Only PAY, HOLD and ABANDON are accepted.
    instruction: 'PENDING',
    idempotency_key: 'instruction-key-4',
})

recordFeeObligationInstruction('obligation-1', {
    instruction: 'PAY',
    idempotency_key: 'instruction-key-5',
    // @ts-expect-error The obligation identity remains a path parameter.
    obligation_id: 'obligation-2',
})

void [
    resultPromise,
    payloadInstruction,
    obligationId,
    activityId,
    serverStatus,
    idempotencyKey,
    reused,
]
