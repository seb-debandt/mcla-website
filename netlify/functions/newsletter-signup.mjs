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

  const headers = {
    Authorization: `Bearer ${apiKey}`,
    "Content-Type": "application/json",
    Accept: "application/json",
  };

  try {
    // Create the contact with tags included in the payload
    const consentDate = new Date().toISOString();
    const contactPayload = {
      first_name,
      last_name,
      emails: [{ value: email, type: "personal" }],
      ...(marketing_consent && {
        tags: ["marketing-consent"],
        note: `Marketing consent given via website newsletter signup on ${consentDate}`,
      }),
    };

    const response = await fetch("https://api.givebutter.com/v1/contacts", {
      method: "POST",
      headers,
      body: JSON.stringify(contactPayload),
    });

    const contactData = await response.json().catch(() => ({}));

    if (!response.ok) {
      console.error("Contact creation failed:", JSON.stringify(contactData));
      return new Response(
        JSON.stringify({
          error: contactData.message || "Failed to create contact",
        }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    // Extract contact ID from response
    const contactId = contactData?.data?.id || contactData?.id;
    console.log("Contact created:", contactId, JSON.stringify(contactData));

    // If tags weren't accepted inline, try the sub-endpoint
    if (contactId && marketing_consent) {
      // Try POST /v1/contacts/{id}/tags
      const tagRes = await fetch(
        `https://api.givebutter.com/v1/contacts/${contactId}/tags`,
        {
          method: "POST",
          headers,
          body: JSON.stringify({ tags: ["marketing-consent"] }),
        }
      ).catch(() => null);

      if (tagRes) {
        const tagBody = await tagRes.text().catch(() => "");
        console.log("Tag response:", tagRes.status, tagBody);
      }

      // Try PUT /v1/contacts/{id} with tags (update approach)
      const updateRes = await fetch(
        `https://api.givebutter.com/v1/contacts/${contactId}`,
        {
          method: "PUT",
          headers,
          body: JSON.stringify({ tags: ["marketing-consent"] }),
        }
      ).catch(() => null);

      if (updateRes) {
        const updateBody = await updateRes.text().catch(() => "");
        console.log("Update response:", updateRes.status, updateBody);
      }
    }

    return new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    console.error("Newsletter signup error:", err);
    return new Response(
      JSON.stringify({ error: "Unable to process request" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
};
