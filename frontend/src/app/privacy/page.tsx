import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy Policy | Historia AI",
  description: "Privacy Policy for Historia AI.",
};

export default function PrivacyPolicy() {
  return (
    <main className="min-h-screen overflow-y-auto bg-[#080704] px-5 py-12 text-[#eee5d7] sm:px-8">
      <article className="mx-auto max-w-3xl rounded-2xl border border-amber-700/30 bg-black/30 p-6 shadow-2xl sm:p-10">
        <Link href="/" className="text-sm text-amber-400 hover:text-amber-300">← Back to Historia AI</Link>
        <h1 className="mt-6 font-serif text-4xl text-amber-100">Privacy Policy</h1>
        <p className="mt-2 text-sm text-white/45">Effective date: September 21, 2026</p>

        <div className="mt-8 space-y-7 text-sm leading-7 text-white/70">
          <section><h2 className="font-serif text-xl text-amber-200">About Historia AI</h2><p className="mt-2">Historia AI is an AI-assisted research experience for exploring Egyptian history through source-grounded conversations.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Information we collect</h2><p className="mt-2">When you sign in with Google, we receive basic account information that you authorize: your name, email address, profile image, and Google account identifier. We do not receive your Google password.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Workspace data</h2><p className="mt-2">If you use cloud sync, Historia AI stores your account identifier and workspace content, which may include chat history, bookmarks, and notes. Questions you submit are processed to generate answers and may be sent to the services used to operate the application.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">How we use information</h2><p className="mt-2">We use this information only to authenticate you, provide and synchronize your workspace, answer your requests, maintain security, and improve the reliability of the service. We do not sell your personal information.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Service providers</h2><p className="mt-2">Historia AI relies on service providers including Google for sign-in and AI services, Supabase for authentication and cloud storage, Vercel for the website, and Render for backend hosting. Their processing is governed by their respective privacy terms.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Data control and deletion</h2><p className="mt-2">You can use the application without cloud sync where available. To request access to or deletion of your cloud account and stored workspace data, contact us using the email below.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Security and retention</h2><p className="mt-2">We use reasonable technical safeguards and retain information only for as long as needed to provide the service, comply with legal obligations, and resolve security issues. No online service can guarantee absolute security.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Children</h2><p className="mt-2">Historia AI is not directed to children under 13, and we do not knowingly collect personal information from children under 13.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Changes</h2><p className="mt-2">We may update this policy as the service changes. The effective date above will be updated when material changes are made.</p></section>
          <section><h2 className="font-serif text-xl text-amber-200">Contact</h2><p className="mt-2">For privacy questions or data requests, email <a className="text-amber-400 hover:text-amber-300" href="mailto:samaareda.sr@gmail.com">samaareda.sr@gmail.com</a>.</p></section>
        </div>
      </article>
    </main>
  );
}
