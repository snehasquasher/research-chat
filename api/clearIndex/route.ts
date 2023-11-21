import { NextResponse } from "next/server";
import { Pinecone } from '@pinecone-database/pinecone'

export async function POST() {
  const pinecone = new Pinecone();
  const index = pinecone.Index(process.env.PINECONE_INDEX!)

  const namespaceName = process.env.PINECONE_NAMESPACE ?? ''
  const namespace = index.namespace(namespaceName)

  // Delete everything within the namespace
  await namespace.deleteAll();

  return NextResponse.json({
    success: true
  })
}