export default async (req) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  const { email, first_name, last_name, marketing_consent } = await req.json();

  if (!email || !first_name || !last_name) {
    return new Response(
      JSON.stringify({ error: "Email, first name, and last name are required" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const apiKey = process.env.GIVEBUTTER_API_KEY;
  if (!apiKey) {
    return new Response(
      JSON.stringify({ error: "Server configuration error" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }

  try {
    // Create the contact
    const contactPayload = {
      first_name,
      last_name,
      emails: [{ value: email, type: "personal" }],
    };

    const response = await fetch("https://api.givebutter.com/v1/contacts", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(contactPayload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return new Response(
        JSON.stringify({
          error: errorData.message || "Failed to create contact",
        }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const contact = await response.json();
    const contactId = contact?.data?.id || contact?.id;

    // Tag the contact with marketing consent and newsletter signup
    if (contactId && marketing_consent) {
      const consentDate = new Date().toISOString();

      // Add tags
      await fetch(`https://api.givebutter.com/v1/contacts/${contactId}/tags`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ tags: ["newsletter", "marketing-consent"] }),
      }).catch(() => {});

      // Add a note recording consent
      await fetch(`https://api.givebutter.com/v1/contacts/${contactId}/notes`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          body: `Marketing consent given via website newsletter signup on ${consentDate}`,
        }),
      }).catch(() => {});
    }

    return new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(
      JSON.stringify({ error: "Unable to process request" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
};
