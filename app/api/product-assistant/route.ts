import { handleAssistant } from '../../../src/server/assistant';
export const runtime='nodejs';
export const maxDuration=60;
export async function POST(request:Request){return handleAssistant('customer',request)}
