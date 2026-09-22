import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms of Service | Historia AI",
  description: "Terms of Service for Historia AI.",
};

export default function TermsOfService() {
  return (
    <main className="min-h-screen overflow-y-auto bg-[#080704] px-5 py-12 text-[#eee5d7] sm:px-8">
      <article className="mx-auto max-w-3xl rounded-2xl border border-amber-700/30 bg-black/30 p-6 shadow-2xl sm:p-10">
        <Link href="/" className="text-sm text-amber-400 hover:text-amber-300">← Back to Historia AI</Link>
        <h1 className="mt-6 font-serif text-4xl text-amber-100">Terms of Service</h1>
        <p className="mt-2 text-sm text-white/45">Effective date: September 21, 2026</p>

        <div className="mt-8 space-y-7 text-sm leading-7 text-white/70">
          <section><h2 className="font-serif text-xl text-amber-200">Acceptance</h2><p className="mt-2">By using Historia AI, you agree to these terms and the Privacy Policy.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Purpose of the service</h2><p className="mt-2">Historia AI provides AI-assisted historical research and educational information. Responses may contain errors or incomplete interpretations and should be checked against the cited sources before academic or professional use.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Your account</h2><p className="mt-2">You are responsible for activity performed through your Google account and for keeping access to that account secure. You must provide accurate account information and use the service lawfully.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Acceptable use</h2><p className="mt-2">Do not misuse the service, interfere with its operation, attempt unauthorized access, upload unlawful material, or use automated requests that place an unreasonable load on the system.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Your content</h2><p className="mt-2">You retain ownership of notes and other content you submit. You grant Historia AI the limited permission needed to process and store that content solely to provide the service.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Availability</h2><p className="mt-2">The service is provided on an “as available” basis. Features may be changed, interrupted, or discontinued, and we cannot guarantee uninterrupted or error-free operation.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Limitation</h2><p className="mt-2">To the extent permitted by law, Historia AI and its developer are not liable for decisions made solely from AI-generated responses or for indirect losses arising from use of the service.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Changes and contact</h2><p className="mt-2">These terms may be updated as the service evolves. Questions can be sent to <a className="text-amber-400 hover:text-amber-300" href="mailto:samaareda.sr@gmail.com">samaareda.sr@gmail.com</a>.</p></section>
        </div>
      </article>
    </main>
  );
}
