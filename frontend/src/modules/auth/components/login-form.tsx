"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { LogIn } from "lucide-react";
import { useForm } from "react-hook-form";

import { LoadingSpinner } from "@/components/feedback/loading-spinner";
import { FormField } from "@/components/forms/form-field";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

import { loginSchema, type LoginFormValues } from "../schemas/auth.schema";
import { useLogin } from "../hooks/use-login";

export function LoginForm() {
  const loginMutation = useLogin();
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" }
  });

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Ingresar a HME Fact</CardTitle>
        <CardDescription>Accede al panel tributario de tu empresa</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={form.handleSubmit((values) => loginMutation.mutate(values))}>
          <FormField label="Correo" error={form.formState.errors.email}>
            <Input type="email" autoComplete="email" {...form.register("email")} />
          </FormField>
          <FormField label="Clave" error={form.formState.errors.password}>
            <Input type="password" autoComplete="current-password" {...form.register("password")} />
          </FormField>
          <Button className="w-full" disabled={loginMutation.isPending}>
            {loginMutation.isPending ? <LoadingSpinner /> : <LogIn className="h-4 w-4" />}
            Entrar
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
